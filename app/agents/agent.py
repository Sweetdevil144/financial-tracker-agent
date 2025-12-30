from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from langchain.messages import AIMessage
from app.database.db import Database
from app.models.agent import ExpenseExtraction, ExpenseValidation
from app.models.collections import Expenses
from app.services.llm_services import LLMService

class ProcessExpenseError(Exception):
    pass


class Agent:
    def __init__(self):
        self.llm_service = LLMService()

    async def parse_expense(self, user_prompt: str) -> dict[str, Any] | AIMessage:
        #  Will later store it in prompt_registry within DB
        system_prompt = self._parse_expense_prompt()
        response = await self.llm_service.parse_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=ExpenseExtraction,
        )
        return response

    async def process_expense(
        self, parsed_data: ExpenseExtraction
    ) -> ExpenseValidation | dict[str, Any] | Any:
        system_prompt = self._validation_prompt()
        user_prompt = parsed_data.model_dump_json()
        result = await self.llm_service.parse_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=ExpenseValidation,
        )
        if isinstance(result, ExpenseValidation):
            if result.is_valid:
                db = Database.get_database()
                if db is None:
                    return ProcessExpenseError("Database not initialized")
                # Random user_id for now : Will be integrated in workflow laater on
                # user_id, amount, currency, merchant, category, date, description, notes, tags
                expense = Expenses(user_id = str(uuid4()), amount = parsed_data.amount, currency = parsed_data.currency, merchant = parsed_data.merchant, category=parsed_data.category, date=datetime.now(timezone.utc))
                res = await db["expenses"].insert_one(expense.model_dump())
                return res
            else:
                return ProcessExpenseError(f"Invalid Parsing : Trying Again. {result.errors}")
                # Retry Logic : To be added later
        # Default Case : dict[Str,Any] -> Fallback
        return ProcessExpenseError("Error : Invalid Response recieved from OpenAI :Retrying again", result)
        # Secondary retyr logic maybe?

    def _validation_prompt(self) -> str:
        return """
                    You are a data sanity checker for expense entries.
                    The assistant will receive a JSON object that follows the **ExpenseExtraction** schema:
                        {
                        "amount": <number>,
                        "currency": "<ISO 4217 code>",
                        "merchant": "<string>",
                        "category": "<string>",
                        "date": "<YYYY‑MM‑DD or ISO string>"
                        }

            The assistant must evaluate the data against the following rules:

            1. **Amount**
            - Alert if the amount is suspiciously high (e.g., > $10 000).
            - A warning should be added to the `warnings` array if the amount exceeds $10 000.

            2. **Currency**
            - Must be a valid ISO 4217 code.
            - If the currency is missing or not recognized, report an error in the `errors` array.

            3. **Category & Merchant**
            - The category should logically match the merchant.
            - If there is a mismatch or the category seems unrelated to the merchant, add a warning stating:
                `"Category '{category}' does not fit typical merchants like '{merchant}'."`

            4. **Date**
            - Must be a valid date string in YYYY‑MM‑DD format.
            - The date cannot be in the future relative to the current date.
            - If the date is missing, malformed, or in the future, add an error to `errors`.

            **Response Format**
            Return a JSON object that satisfies our internal **ExpenseValidation** schema as following:

            ```json
            {
            "is_valid": true|false,
            "errors": [ ... ], // array of error messages
            "warnings": [ ... ], // array of warning messages
            "data": { ... }// the original parsed data
            }
            The assistant must output **only** this JSON object—no additional text, comments, or formatting.
            """

    def _parse_expense_prompt(self) -> str:
        return """
        ## System Prompt for Expense Data Extraction

        You are a powerful language model tasked with extracting structured expense data from informal text.
        Provide a **JSON object** that follows the schema below.  If a field is not present in the input, use the default values specified.

        ### Extraction Schema

        | Field    | Description                                                        | Default                |
        |----------|--------------------------------------------------------------------|------------------------|
        | `amount` | Numeric amount spent (float).                                      | —                      |
        | `currency` | Currency code (ISO 4217). Example: `USD`, `EUR`, `GBP`.         | `USD` if omitted.      |
        | `merchant` | Business or store name.                                           | —                      |
        | `category` | High‑level category of the expense. Use the mappings provided.  | `Uncategorized` if no match. |
        | `date`   | Date of purchase in ISO 8601 format (`YYYY-MM-DD`). If the text contains relative dates such as `yesterday`, `today`, or days of the week, convert them to the correct ISO date.  | Date of extraction (`YYYY-MM-DD`). |

        ### Category Mappings

        | Category          | Keywords (case‑insensitive)                                  |
        |-------------------|--------------------------------------------------------------|
        | `Food & Dining`   | restaurant, cafe, coffee, snack, lunch, dinner              |
        | `Transportation` | taxi, uber, bus, train, flight, parking, toll               |
        | `Shopping`        | mall, supermarket, clothing, electronics, online shop      |
        | `Entertainment`  | movie, concert, theater, streaming, tickets                 |
        | `Utilities`       | electricity, water, internet, cable                        |
        | `Health & Wellness` | pharmacy, medicine, gym, doctor, dental                 |
        | `Professional Services` | lawyer, accountant, consultant, freelancer      |
        | `Travel`          | hotel, flight, accommodation, itinerary                    |
        | `Other`           | Miscellaneous items not fitting above categories             |

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
           "amount": 12.5,
           "currency": "USD",
           "merchant": "Starbucks",
           "category": "Food & Dining",
           "date": "2024-03-13"
         }
         ```

         **Input**
         `"Booked a flight on March 15th for €350."`
         **Output**
         ```json
         {
           "amount": 350,
           "currency": "EUR",
           "merchant": "Airline",
           "category": "Travel",
           "date": "2024-03-15"
         }
         ```

         **Input**
         `"Paid the electric bill of $200 last Thursday."`
         **Output**
         ```json
         {
           "amount": 200,
           "currency": "USD",
           "merchant": "Electric Company",
           "category": "Utilities",
           "date": "2024-03-14"
         }
         ```

        ### Instructions for the Language Model

        1. **Identify and extract** each field listed in the schema; cast numeric values to float.
        2. **Normalize currency**: if the currency symbol ($, €, £) is present, map to `USD`, `EUR`, `GBP` respectively; otherwise, use the default `USD`.
        3. **Map merchant to category** using the keyword table; if no match, set `category` to `Other`.
        4. **Parse dates** with the rules above. If relative, compute the ISO date; if absolute (e.g., `March 15th`), parse to `YYYY-MM-DD`. If parsing fails, use the extraction date.
        5. **Return a single JSON object** exactly as specified. If multiple expenses are detected in a single input, return a JSON array of objects.
        6. **Do not add any extraneous text**—only output the JSON.
        """


#   User Input (raw text)
#       ↓
#   [AI Agent 1: Parser/Extractor]
#       ↓ (structured JSON)
#   {amount, currency, date, merchant, category, ...}
#       ↓
#   [AI Agent 2: Processor/Validator]
#       ↓
#   Database Storage + Response
