from datetime import datetime, timezone
from uuid import uuid4

from app.database.db import Database
from app.models.agent import ExpenseExtraction, ExpenseResponse, ExpenseValidation
from app.models.collections import Expenses
from app.services.llm_services import LLMService
from app.utils.log import logger
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class Agent:
    def __init__(self):
        self.llm_service = LLMService()

    async def parse_expense(self, user_prompt: str, user_id: str) -> ExpenseExtraction:
        #  Will later store it in prompt_registry within DB
        system_prompt = self._parse_expense_prompt()
        response = await self.llm_service.parse_structured(
            system_prompt=system_prompt,
            user_prompt=f" Expense Information : {user_prompt}. user_id : {user_id}",
            output_schema=ExpenseExtraction,
        )
        try:
            response = ExpenseExtraction.model_validate(response)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse expense correctly",
            ) from e

    async def process_expense(self, parsed_data: ExpenseExtraction) -> ExpenseResponse:
        system_prompt = self._validation_prompt()
        user_prompt = parsed_data.model_dump_json()
        result = await self.llm_service.parse_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=ExpenseValidation,
        )
        try:
            expense_id = str(uuid4())
            result = ExpenseValidation.model_validate(result)
            if result.is_valid:
                db = Database.get_database()
                if db is None:
                    return ExpenseResponse(
                        success=False,
                        message="Expense Insertion Failed due to Lack of DB Connection",
                        expense_id=None,
                    )
                expense = Expenses(
                    _id=expense_id,
                    user_id=parsed_data.user_id,
                    amount=parsed_data.amount,
                    currency=parsed_data.currency,
                    merchant=parsed_data.merchant,
                    category=parsed_data.category,
                    date=parsed_data.date,
                    created_at=str(datetime.now(timezone.utc)),
                )
                res = await db["expenses"].insert_one(
                    expense.model_dump(by_alias=True, mode="json")
                )
                if res.acknowledged:
                    return ExpenseResponse(
                        expense_id=expense_id,
                        success=True,
                        message="Insertion successful",
                        errors=result.errors,
                        warnings=result.warnings,
                    )
                return ExpenseResponse(
                    success=False,
                    message="Expense Insertion Failed. Failed to acknowledge",
                    errors=result.errors,
                    warnings=result.warnings,
                    expense_id=expense_id,
                )
            else:
                logger.warning(
                    f"Invalid expense structure. Not inserting Data \nErrors : {result.errors}\nWarnings{result.warnings}"
                )
                return ExpenseResponse(
                    success=False,
                    message="Expense Insertion Failed",
                    errors=result.errors,
                    warnings=result.warnings,
                    expense_id=expense_id,
                )
                # Retry Logic : To be added later
        except Exception as e:
            return ExpenseResponse(
                success=False,
                message=f"Expense Insertion Failed with error : {e}",
                expense_id=None,
            )
        # Secondary retry logic maybe?

    def _validation_prompt(self) -> str:
        base_prompt = """
                    You are a data sanity checker for expense entries.
                    The assistant will receive a JSON object that follows the **ExpenseExtraction** schema:
                        {
                        "amount": <number>,
                        "currency": "<ISO 4217 code>",
                        "merchant": "<string>",
                        "category": "<string>",
                        "date": "<YYYY‑MM‑DD or ISO string>"
                        }

            The assistant must output **only** this JSON object—no additional text, comments, or formatting.

            1. **Amount Validation**
            - **ERROR**: Negative amounts (e.g., -100.00) - clearly malicious/invalid
            - **ERROR**: Amounts less than $0.01 - no valid expense has fractions of a cent
            - **ERROR**: Unrealistically large amounts > $1,000,000 - clearly unrealistic for typical expenses
            - **WARNING**: Amount equals 0.00 - suspicious but possibly legitimate for refunds/adjustments
            - **WARNING**: High amounts > $10,000 - add warning: "Suspiciously high amount: ${amount}"
            - **WARNING**: More than 2 decimal places (e.g., 12.345) - currencies typically don't need more precision

            2. **Currency Validation**
            - **ERROR**: Must be a valid ISO 4217 code (e.g., USD, INR, JPY, EUR, GBP)
            - **ERROR**: If currency is missing or not recognized, report error: "Invalid currency code: {currency}"

            3. **Required Fields Validation**
            - **ERROR**: merchant cannot be empty string ("") or null - this is a required business field
            - **ERROR**: user_id cannot be empty string ("") or null - this is a required business field
            - **ERROR**: Any required field missing or null should be flagged as error

            4. **Category & Merchant Validation**
            - **WARNING**: The category should logically match the merchant
            - **WARNING**: If mismatch detected, add warning: "Category '{category}' does not fit typical merchants like '{merchant}'."
            - **ERROR**: Empty merchant name - this is invalid
            - **WARNING**: Suspicious merchant names:
              - Only 1-2 characters (e.g., "a", "xy")
              - Repeated characters (e.g., "aaaaaa", "zzzzzz")
              - Only numbers (e.g., "123456", "999999")
            - **WARNING**: Specific merchant-category mismatch rules:
              - Amazon should be Shopping (not Entertainment/Other)
              - Uber/Lyft should be Transportation (not Food & Dining)
              - Starbucks/Dunkin should be Food & Dining (not Other)

            5. **Date Validation**
            - Must be a valid date string in YYYY‑MM‑DD format.
            - **Past dates are completely valid and expected**. Users commonly submit expenses from previous days, weeks, or months.
            - Allow up to 2 years in the past from the current date.
            - Allow up to 1 year in the future from the current date.
            - **ERROR** for unrealistic dates:
              - Dates more than 2 years in the past
              - Dates more than 1 year in the future
              - Malformed or missing dates
            - Example: If today is 2026-01-24, a date of 2024-01-25 (2 years past) is valid, but 2015-01-01 is unrealistic. A date of 2027-01-25 (1 year future) is valid, but 2060-01-01 is unrealistic.

            6. **Security Pattern Detection**
            - **ERROR**: SQL injection attempts:
              - "; DROP TABLE", "OR 1=1", "UNION SELECT", "'--", "admin'--"
            - **ERROR**: XSS/Script injection attempts:
              - "<script>", "javascript:", "onerror=", "onload=", "onclick="
            - **ERROR**: Shell/command injection attempts:
              - "; rm -rf", "| cat /etc/passwd", "; ls -la", "$(whoami)"
            - **ERROR**: Any field contains obvious attack patterns - set is_valid=false immediately

            7. **Text Field Validation**
            - **WARNING**: Description > 500 characters - possibly spam or excessive text
            - **WARNING**: Note > 1000 characters - excessive length
            - **WARNING**: Description or note contains test data keywords: "test", "sample", "demo", "placeholder", "todo", "xxx"

            8. **Test Data Detection**
            - **WARNING**: Merchant contains test patterns: "test", "sample", "demo", "xxx", "placeholder", "123456", "000000"
            - **WARNING**: Amount is exactly $1,000,000 - suspicious but possible
            - **WARNING**: Date is exactly 1 year from today - valid but unusual pattern

            9. **Validation Rules Summary**
            - **ERRORS** (must set `is_valid=false`):
              - Negative amounts (< 0)
              - Amounts less than $0.01
              - Unrealistically large amounts (>$1,000,000)
              - Missing or empty required fields (merchant, user_id)
              - Unrecognized currency codes
              - Unrealistic dates (more than 2 years past or more than 1 year future)
              - Security attack patterns (SQL injection, XSS, shell injection)
              - Malformed or invalid data
              - Suspicious or clearly malicious entries
              - Ambiguous or nonsensical data that appears to be system abuse attempts
            - **WARNINGS** (do NOT affect `is_valid`):
              - High amounts (> $10,000)
              - Zero amounts (= 0)
              - Category/merchant mismatches
              - More than 2 decimal places
              - Suspicious merchant names (too short, repeated chars, only numbers)
              - Long text fields (>500 char description, >1000 char note)
              - Test data patterns ("test", "sample", "demo", etc.)
              - Unusual but legitimate expense patterns
            - **IMPORTANT**: Warnings should NEVER cause `is_valid` to be false. Only critical errors should set `is_valid=false`.

            **Response Format**
            Return a JSON object that satisfies our internal **ExpenseValidation** schema as following:

            **ALL four fields are MANDATORY. Never omit any field.**
            - `is_valid` - REQUIRED, must be boolean (true/false)
            - `errors` - REQUIRED, must be array of strings (can be empty [])
            - `warnings` - REQUIRED, must be array of strings (can be empty [])
            - `data` - REQUIRED, must contain the original parsed expense data object

            ❌ WRONG (missing fields):
            ```json
            {
              "data": {"amount": 100, "currency": "USD", "merchant": "Store", "category": "Shopping", "date": "2026-03-15"}
            }
            ```

            ✅ CORRECT (all fields present):
            ```json
            {
              "is_valid": true,
              "errors": [],
              "warnings": [],
              "data": {"amount": 100, "currency": "USD", "merchant": "Store", "category": "Shopping", "date": "2026-03-15"}
            }
            ```

            The assistant must output **only** this JSON object—no additional text, comments, or formatting.
            """

        context = f"""

            ### Current Reference Information
            - **Current Date**: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
            - **Current Day**: {datetime.now(timezone.utc).strftime("%A")}
            - **Current Year**: {datetime.now(timezone.utc).year}
            - Use this information to validate that expense dates are not in the future
            """

        return base_prompt + context

    def _parse_expense_prompt(self) -> str:
        base_prompt = """
        ## System Prompt for Expense Data Extraction

        You are a powerful language model tasked with extracting structured expense data from informal text.
        Provide a **JSON object** that follows the schema below.  If a field is not present in the input, use the default values specified.

        ### Extraction Schema

        **ALL fields are MANDATORY and must be present in every response.**

        | Field       | Type     | Description                                                        | Required | Notes |
        |-------------|----------|--------------------------------------------------------------------|----------|-------|
        | `user_id`   | string   | User identifier (provided in input)                                | YES      | Must be extracted from input |
        | `amount`    | float    | Numeric amount spent                                              | YES      | Must be > 0 |
        | `currency`  | string   | Currency code (ISO 4217). Example: `USD`, `EUR`, `GBP`.         | YES      | Default: `USD` if not specified |
        | `merchant`  | string   | Business or store name                                           | YES      | — |
        | `category`  | string   | High‑level category of the expense (use mappings below)           | YES      | Must be from predefined list or `Other` |
        | `date`      | string   | Date of purchase in ISO 8601 format (`YYYY-MM-DD`)              | YES      | Convert relative dates (yesterday, today) |
        | `description`| string   | Brief description of the expense                                  | YES      | Use empty string `""` if not provided |
        | `note`      | string   | Additional notes or comments                                      | YES      | Use empty string `""` if not provided |

        ### Category Mappings

        **IMPORTANT**: You MUST use ONLY these predefined categories. Do NOT create new categories or invent category names. Select the closest matching category from this list. If no clear match exists, use `Other`.

        | Category          | Keywords (case‑insensitive)                                  |
        |-------------------|--------------------------------------------------------------|
        | `Food & Dining`   | restaurant, cafe, coffee, snack, lunch, dinner, breakfast, brunch, bar, pub, grill, bistro, diner, food court, food truck, pizza, burger, sushi, bakery, ice cream, meal, drink, beverage, dining, eatery, cafeteria, deli |
        | `Transportation` | taxi, uber, lyft, bus, train, flight, parking, toll, gas, fuel, metro, subway, tram, bike, scooter, rental car, car service, rideshare, transit, commute, transport, airline, airport, station |
        | `Shopping`        | mall, supermarket, grocery, clothing, fashion, shoes, accessories, electronics, gadgets, appliances, furniture, home goods, online shop, e-commerce, retail, store, department store, amazon, walmart, target, best buy |
        | `Entertainment`  | movie, concert, theater, streaming, tickets, netflix, spotify, youtube, hulu, disney+, games, gaming, casino, amusement park, zoo, museum, event, show, performance, leisure, hobbies, sports, recreation |
        | `Utilities`       | electricity, water, internet, cable, phone, mobile, cellular, gas, trash, waste, sewage, heating, cooling, hvac, utilities, power, energy, broadband, wifi |
        | `Health & Wellness` | pharmacy, medicine, pharmacy, drugstore, doctor, physician, dentist, dental, medical, hospital, clinic, health, wellness, fitness, gym, yoga, pilates, spa, massage, therapy, mental health, insurance, healthcare |
        | `Professional Services` | lawyer, attorney, accountant, bookkeeper, consultant, freelancer, contractor, architect, engineer, designer, marketing, advertising, software, it services, business services, legal, financial advisor, taxes |
        | `Travel`          | hotel, flight, airline, accommodation, booking, airbnb, resort, vacation, trip, travel agency, tourism, rental, car rental, luggage, airport, cruise, travel insurance, transport, transportation |
        | `Other`           | Miscellaneous items not fitting above categories, uncategorized, general, donation, charity, gift, cash, atm, bank, fees, charges, miscellaneous |

        ### Handling Dates

        - Recognize relative expressions:
          - `yesterday` → previous calendar day
          - `today` → current day
          - `last <weekday>` (e.g., `last Thursday`) → most recent occurrence before today
          - `<ordinal> <weekday>` (e.g., `on the 5th Monday`) → the date corresponding to that week in the current month (use current month unless the date is already past, then assume next month)
        - Convert all dates to `YYYY-MM-DD`.
        - If no date can be determined, use the extraction date as the default.

        ### Example Prompt

         **Input**
         `"I paid $12.50 at Starbucks for a latte yesterday."`
         **Output**
         ```json
         {
           "user_id": "test_user",
           "amount": 12.5,
           "currency": "USD",
           "merchant": "Starbucks",
           "category": "Food & Dining",
           "date": "2026-03-13",
           "description": "",
           "note": ""
         }
         ```

         **Input**
         `"Booked a flight on March 15th for €350."`
         **Output**
         ```json
         {
           "user_id": "test_user",
           "amount": 350,
           "currency": "EUR",
           "merchant": "Airline",
           "category": "Travel",
           "date": "2026-03-15",
           "description": "Flight booking",
           "note": ""
         }
         ```

         **Input**
         `"Paid the electric bill of $200 last Thursday."`
         **Output**
         ```json
         {
           "user_id": "test_user",
           "amount": 200,
           "currency": "USD",
           "merchant": "Electric Company",
           "category": "Utilities",
           "date": "2026-03-14",
           "description": "Monthly electric bill",
           "note": "Paid on time"
         }
         ```

        ### Instructions for the Language Model

        1. **MUST include ALL 8 fields** (user_id, amount, currency, merchant, category, date, description, note) in every response. Never omit any field.
        2. **Extract user_id** from the input text explicitly provided.
        3. **Identify and extract** each field listed in the schema; cast numeric values to float.
        4. **Normalize currency**: if the currency symbol ($, €, £) is present, map to `USD`, `EUR`, `GBP` respectively; otherwise, use the default `USD`.
        5. **Map merchant to category** using the keyword table; if no match, set `category` to `Other`.
        6. **Parse dates** with the rules above. If relative, compute the ISO date; if absolute (e.g., `March 15th`), parse to `YYYY-MM-DD`. If parsing fails, use the extraction date.
        7. **For description and note fields**: If no information is provided in the input, use an empty string `""`. Do NOT omit these fields.
        8. **Return a single JSON object** exactly as specified with ALL 8 fields present.
        9. **Do not add any extraneous text**—only output the JSON.
        """

        context = f"""

        ### Current Reference Information
        - **Current Date**: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
        - **Current Day**: {datetime.now(timezone.utc).strftime("%A")}
        - **Current Year**: {datetime.now(timezone.utc).year}
        - Use this as reference point for relative date calculations and date parsing
        """

        return base_prompt + context


#   User Input (raw text)
#       ↓
#   [AI Agent 1: Parser/Extractor]
#       ↓ (structured JSON)
#   {amount, currency, date, merchant, category, ...}
#       ↓
#   [AI Agent 2: Processor/Validator]
#       ↓
#   Database Storage + Response

agent = Agent()
