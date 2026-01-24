# Personal Finance Intelligence Agent

## Prompt

You are my CODING JOURNEY GUIDE helping me across problems like "What to do next", "How to do next", with minimal code support(almost nil code form your side). Only I will write code by my hand. Critical : I need minimal code assistance from your side. your role is that of a technical guide, or a mentor to be precise who will guide me in completing project.

## Product Overview

An AI-powered expense tracking SaaS that uses Large Language Models to help users log expenses, analyze spending patterns, manage budgets, and receive financial insights through natural language interaction.

## Problem Statement

Most people fail to track expenses consistently due to friction in the process. This agent removes that friction by:
- Accepting natural language input instead of forms
- Automatically categorizing transactions
- Providing instant analytics and insights
- Managing budgets with real-time alerts

## Core Capabilities

### 1. Expense Management
- Natural language expense entry
- Automatic categorization by merchant/description
- Multi-currency support with conversion
- Extraction of amount, merchant, category, and date from unstructured text

### 2. Financial Analytics
- Spending analysis by category and time period
- Month-over-month comparisons
- Top merchants and spending patterns
- Unusual transaction detection

### 3. Budget Intelligence
- Category-based budget setting
- Real-time budget tracking
- Utilization alerts (80%, 100% thresholds)
- Budget recommendations based on historical spending

### 4. Query Interface
- Complex natural language queries
- Date range filtering
- Amount-based filtering
- Category and merchant search

## Database Architecture

### Collections

**expenses**
- user_id, amount, currency, converted_amount_usd
- description, merchant, category
- date, created_at
- tags, notes

**budgets**
- user_id, category, amount, currency
- period (monthly/weekly)
- start_date, created_at

**user_preferences**
- user_id, default_currency
- categories list

## Technical Roadmap

### Phase 1: Foundation ✅ COMPLETED

**Database Setup**
- ✅ Set up MongoDB with Motor (async driver)
- ✅ Create collections with proper indexes
- ✅ Implement Pydantic schema validation
- ✅ Create connection module with lazy initialization and error handling

**Agent Architecture**
- ✅ Initialize LangChain with Azure OpenAI
- ✅ Set up structured output using Pydantic schemas
- ✅ Create base Agent class with two-step AI workflow
- ✅ Implement LLM service layer with retry logic

**CRUD Operations**
- ✅ Implement core database operations (insert_one, insert_many, read_one, query_read, update_one, delete)
- ✅ Add comprehensive error handling
- ✅ Create reusable functions for all tools

**User Context & Authentication**
- ✅ JWT-based authentication
- ✅ User context extraction from requests
- ✅ Development mode with test user

### Phase 2: AI-Powered Parsing ✅ COMPLETED

**Architecture Decision: Two-Agent AI Workflow**

Instead of regex-based parsing, this system uses a sophisticated two-agent AI approach:

**Agent 1: Expense Parser (parse_expense)**
- Accepts raw natural language text
- Uses LLM with structured output to extract:
  - Amount (float)
  - Currency (ISO 4217 code)
  - Merchant name
  - Category (auto-categorized using AI understanding)
  - Date (handles relative dates: "yesterday", "last Thursday", etc.)
  - Optional: description and notes
- Powered by external prompt template (parse_expense.md)
- Returns validated ExpenseExtraction Pydantic model

**Agent 2: Validator & Processor (process_expense)**
- Receives ExpenseExtraction from Agent 1
- AI validates data against business rules:
  - Amount validation (negative, zero, suspiciously high >$10,000)
  - Currency code validation (ISO 4217)
  - Category-merchant logical matching
  - Date validation (no future dates, proper format)
  - Empty merchant detection
- Returns ExpenseValidation with is_valid flag, errors[], warnings[]
- If valid: stores in MongoDB expenses collection
- If invalid: returns detailed error messages

**Why AI Instead of Regex?**
- **Better accuracy**: AI understands context ("fifty dollars" → $50.00)
- **Handles ambiguity**: "coffee at Starbucks yesterday" → correctly extracts all fields
- **Auto-categorization**: Merchant → Category mapping using semantic understanding
- **Relative dates**: "last Thursday" → actual ISO date based on current date
- **Extensible**: Easy to add new rules via prompt engineering
- **Multi-language support**: Can be extended to non-English inputs

### Phase 3: Core Tools Implementation 🔄 IN PROGRESS

Tools are business logic wrappers around the Agent class. They orchestrate workflows and provide clean interfaces for API routes.

**Tool: add_expense** (app/tools/expense_tools.py)
- Accept user_id + raw natural language text
- Call Agent.parse_expense(text) → ExpenseExtraction
- Call Agent.process_expense(parsed_data) → ExpenseResponse
- Return structured response with success/errors/warnings
- Handle edge cases: empty input, LLM timeouts, DB failures

**Tool: list_expenses** (app/tools/expense_tools.py)
- Accept filters: user_id, date_range, category, merchant, amount_range
- Build MongoDB aggregation pipeline
- Support pagination (limit, offset)
- Support sorting (by date, amount, merchant)
- Return list of expense dictionaries with formatted dates

**Tool: update_expense** (app/tools/expense_tools.py)
- Accept expense_id + fields to update
- Validate user owns the expense
- Update specific fields (amount, merchant, category, etc.)
- Return updated expense

**Tool: delete_expense** (app/tools/expense_tools.py)
- Accept user_id + expense_id
- Validate ownership
- Soft delete OR hard delete from MongoDB
- Return success confirmation

**Tool: analyze_spending** (app/tools/analytics_tools.py)
- Calculate category-wise totals for time period
- Generate percentage breakdowns
- Month-over-month comparisons
- Top N merchants by spending
- Average daily/weekly/monthly spending
- Use MongoDB aggregation framework

**Tool: manage_budget** (app/tools/budget_tools.py)
- CRUD operations for budgets (create, read, update, delete)
- Calculate current spending vs budget
- Calculate utilization percentage
- Flag warnings (>80%) and alerts (>100%)
- Support multiple budget periods (weekly, monthly, yearly)

**Tool: get_budget_status** (app/tools/budget_tools.py)
- For each active budget, calculate current spending
- Compare against budget amount
- Return list with utilization percentages
- Include warnings/alerts

### Phase 4: API Layer (FastAPI Routes) ⏳ PENDING

**Expense Routes** (app/api/routes/expenses.py)
- POST /api/v1/expenses - Add expense (calls add_expense tool)
- GET /api/v1/expenses - List expenses with filters
- GET /api/v1/expenses/{id} - Get single expense
- PUT /api/v1/expenses/{id} - Update expense
- DELETE /api/v1/expenses/{id} - Delete expense
- All routes extract user_id from JWT token

**Analytics Routes** (app/api/routes/analytics.py)
- GET /api/v1/analytics/spending - Spending breakdown by category
- GET /api/v1/analytics/trends - Month-over-month trends
- GET /api/v1/analytics/merchants - Top merchants analysis

**Budget Routes** (app/api/routes/budgets.py)
- POST /api/v1/budgets - Create budget
- GET /api/v1/budgets - List all budgets for user
- GET /api/v1/budgets/{id} - Get single budget
- PUT /api/v1/budgets/{id} - Update budget
- DELETE /api/v1/budgets/{id} - Delete budget
- GET /api/v1/budgets/status - Get all budget statuses with utilization

**Error Handling Middleware**
- Global exception handler for all routes
- Database connection error → 503
- Validation errors → 422
- LLM timeout → 500
- Not found → 404
- Unauthorized → 401

### Phase 5: Advanced Features (Day 3)

**Insights Generation**
- Detect spending trends
- Identify unusual transactions
- Compare against averages
- Generate recommendations
- Predict monthly spending

**Budget Alerts**
- Check utilization thresholds
- Generate warning messages
- Provide actionable suggestions
- Track alert history

**Query Enhancement**
- Support complex date expressions
- Handle ambiguous queries
- Implement query clarification
- Add query suggestions

### Phase 6: Interface (Day 3)

**CLI Interface**
- Create command-line interaction loop
- Add colored output
- Implement formatted tables
- Add progress indicators

**Streamlit UI (Optional)**
- Design main dashboard
- Create expense entry form
- Build analytics visualizations
- Add budget tracking views
- Implement chat interface

### Phase 7: Testing & Refinement (Day 3)

**Test Scenarios**
- Various natural language expense formats
- Edge cases (invalid amounts, ambiguous dates)
- Multi-currency transactions
- Complex analytical queries
- Budget threshold testing

**Data Population**
- Create sample expense data
- Set up realistic spending patterns
- Test with multiple months of data
- Verify analytics accuracy

**Performance Optimization**
- Add database indexes
- Implement query optimization
- Cache frequent calculations
- Optimize LLM token usage

## Technical Stack

**Core Components**
- Python 3.11+
- FastAPI (async web framework)
- LangChain (LLM orchestration)
- Azure OpenAI (GPT-4 with structured output)
- MongoDB Atlas with Motor (async database driver)
- Pydantic v2 (data validation)

**Key Libraries**
- `motor` - Async MongoDB driver
- `langchain-openai` - Azure OpenAI integration
- `python-dotenv` - Environment configuration
- `pyjwt` - JWT authentication
- `uvicorn` - ASGI server
- `pydantic` - Schema validation

**Architecture Patterns**
- Two-agent AI workflow (parse → validate → store)
- Structured output using Pydantic schemas
- Async/await throughout (non-blocking I/O)
- Repository pattern (CRUD layer abstraction)
- JWT-based authentication
- External prompt management (markdown files)

## Project Structure

```
agent/
├── app/
│   ├── agents/
│   │   └── agent.py              # Two-agent AI workflow (parse + validate)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── expenses.py       # Expense CRUD endpoints (TODO)
│   │       ├── analytics.py      # Analytics endpoints (TODO)
│   │       └── budgets.py        # Budget endpoints (TODO)
│   ├── config/
│   │   ├── config.py             # Environment config & secrets
│   │   └── exceptions.py         # Custom exceptions
│   ├── database/
│   │   ├── db.py                 # MongoDB connection (Motor)
│   │   └── core_data.py          # CRUD operations layer
│   ├── models/
│   │   ├── agent.py              # AI agent schemas (ExpenseExtraction, etc.)
│   │   ├── collections.py        # MongoDB document schemas
│   │   └── user.py               # User model
│   ├── prompts/
│   │   ├── parse_expense.md      # LLM prompt for expense parsing
│   │   └── process_expense.md    # LLM prompt for validation
│   ├── services/
│   │   ├── llm_services.py       # LangChain + Azure OpenAI integration
│   │   └── user_context.py       # JWT authentication & user extraction
│   ├── static/
│   │   └── localization.py       # Error messages
│   ├── tests/
│   │   └── test_agent.py         # Unit tests (TODO)
│   ├── tools/
│   │   ├── expense_tools.py      # Business logic for expenses (TODO)
│   │   ├── analytics_tools.py    # Analytics logic (TODO)
│   │   └── budget_tools.py       # Budget management logic (TODO)
│   ├── utils/
│   │   ├── enums.py              # Currencies, BudgetPeriod enums
│   │   └── log.py                # Logging configuration
│   └── main.py                   # FastAPI app entry point
├── requirements.txt
├── .env
└── README.md
```

## Implementation Priorities

**Must Have**
- Natural language expense entry
- Automatic categorization
- Basic analytics (totals, breakdowns)
- Budget tracking
- MongoDB persistence

**Should Have**
- Multi-currency support
- Month-over-month comparisons
- Budget alerts
- Complex queries

**Nice to Have**
- Spending insights and predictions
- Streamlit UI
- Receipt OCR
- Export functionality

## Key Design Decisions

**Why AI-Powered Parsing (vs Regex)**
- **Context understanding**: "fifty bucks at Starbucks" → correctly extracts all fields
- **Auto-categorization**: Semantic understanding of merchant → category mapping
- **Relative dates**: "yesterday", "last Friday" → actual ISO dates
- **Extensibility**: New rules via prompt engineering, not code changes
- **Accuracy**: Handles ambiguous inputs better than regex patterns
- **Validation**: AI validates business logic (category-merchant match, future dates)

**Why Two-Agent Architecture**
- **Separation of concerns**: Parsing vs validation as distinct responsibilities
- **Better error handling**: Detailed errors/warnings from validation agent
- **Testability**: Each agent can be tested independently
- **Prompt specialization**: Each agent has focused, optimized prompts
- **Flexibility**: Can swap/upgrade agents independently

**Why LangChain + Azure OpenAI**
- Structured output via Pydantic (guarantees valid JSON)
- Built-in retry logic and error handling
- Azure enterprise compliance and security
- Reasoning capabilities for complex validation
- Easy integration with FastAPI async patterns

**Why MongoDB**
- Flexible schema for evolving features
- Powerful aggregation framework (perfect for analytics)
- Excellent date-based query performance
- Motor provides async driver (matches FastAPI)
- JSON-like documents (natural fit for Pydantic models)

**Why FastAPI**
- Native async/await support (non-blocking I/O)
- Automatic OpenAPI documentation
- Pydantic integration for request/response validation
- High performance (comparable to Node.js)
- Modern Python best practices

**Tool Design Philosophy**
- Tools are thin wrappers around Agent + database operations
- Each tool has single responsibility
- Tools handle business logic, not AI logic (AI is in Agent)
- Clear input/output contracts using Pydantic
- Comprehensive error handling and logging

## Success Metrics

**Functional**
- Accurate expense parsing (>90%)
- Correct categorization (>85%)
- Successful multi-currency conversion
- Accurate budget calculations

**Technical**
- Response time <3 seconds for simple queries
- Database queries optimized with indexes
- Error handling covers edge cases
- Clean separation of concerns

**User Experience**
- Conversational and intuitive
- Clear error messages
- Formatted, readable output
- Handles ambiguous input gracefully

## Future Enhancements

**Phase 2 Features**
- Recurring expense detection
- Bill reminders
- Savings goals tracking
- Split expense management

**Advanced Analytics**
- Spending predictions using ML
- Anomaly detection
- Peer comparisons
- Investment tracking integration

**Integration Opportunities**
- Bank account connection (Plaid API)
- Credit card import
- Receipt scanning (OCR)
- Export to accounting software

## Development Timeline

**Day 1: Foundation**
- Hours 1-3: Database setup and schema
- Hours 4-6: Agent initialization and basic tool
- Hours 7-8: NLP parser foundation

**Day 2: Core Features**
- Hours 1-4: Complete all tool implementations
- Hours 5-6: Agent integration and testing
- Hours 7-8: Error handling and refinement

**Day 3: Polish**
- Hours 1-3: Advanced features (insights, alerts)
- Hours 4-6: UI implementation
- Hours 7-8: Testing and documentation

## Notes

This is a personal project to understand agent-based systems and practical AI applications. Focus is on building a functional MVP that demonstrates core concepts: natural language understanding, tool usage, database integration, and conversational AI.

The goal is not production readiness but learning through implementation. Code quality, proper architecture, low-latency, optimized code quality, and documentation are priorities for future reference and potential expansion.

## Resources

### LangChain
- [LangChain Documentation](https://docs.langchain.com/)
- [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [Custom Tools](https://docs.langchain.com/oss/python/langchain/tools)
- [Memory Management](https://docs.langchain.com/oss/python/concepts/memory#memory-overview)
