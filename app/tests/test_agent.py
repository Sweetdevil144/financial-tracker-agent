"""
Comprehensive tests for Personal Finance Intelligence Agent

Run with: pytest app/tests/test_agent.py -v
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.agent import ExpenseExtraction, ExpenseResponse, ExpenseValidation
from app.models.budgets import CreateBudget
from app.models.budgets import UpdateOne as BudgetUpdateOne
from app.models.collections import Budgets, Expenses
from app.models.expenses import CreateExpense
from app.models.expenses import UpdateOne as ExpenseUpdateOne
from app.utils.enums import BudgetPeriod, Currencies


class TestEnums:
    def test_currencies_values(self):
        assert Currencies.USD.value == "USD"
        assert Currencies.EUR.value == "EUR"
        assert Currencies.INR.value == "INR"
        assert Currencies.GBP.value == "GBP"
        assert Currencies.JPY.value == "JPY"

    def test_budget_period_values(self):
        assert BudgetPeriod.DAILY.value == "daily"
        assert BudgetPeriod.WEEKLY.value == "weekly"
        assert BudgetPeriod.MONTHLY.value == "monthly"
        assert BudgetPeriod.YEARLY.value == "yearly"


class TestExpenseModels:
    def test_expense_extraction_valid(self):
        expense = ExpenseExtraction(
            user_id="test_user",
            amount=50.0,
            currency=Currencies.USD,
            merchant="Starbucks",
            category="Food & Dining",
            date="2024-01-15",
        )
        assert expense.amount == 50.0
        assert expense.currency == Currencies.USD
        assert expense.merchant == "Starbucks"
        assert expense.user_id == "test_user"

    def test_expense_extraction_defaults(self):
        expense = ExpenseExtraction(
            user_id="test_user",
            amount=25.0,
            category="Other",
            date="2024-01-15",
        )
        assert expense.currency == Currencies.USD
        assert expense.merchant is None
        assert expense.description == ""
        assert expense.note == ""

    def test_expense_validation_valid(self):
        validation = ExpenseValidation(
            is_valid=True,
            errors=[],
            warnings=["Amount is high"],
        )
        assert validation.is_valid is True
        assert validation.warnings is not None
        assert len(validation.warnings) == 1

    def test_expense_validation_invalid(self):
        validation = ExpenseValidation(
            is_valid=False,
            errors=["Invalid date", "Missing amount"],
            warnings=[],
        )
        assert validation.is_valid is False
        assert validation.errors is not None
        assert len(validation.errors) == 2

    def test_expense_response_success(self):
        response = ExpenseResponse(
            success=True,
            message="Expense added",
            expense_id="abc-123",
        )
        assert response.success is True
        assert response.expense_id == "abc-123"

    def test_expense_response_failure(self):
        response = ExpenseResponse(
            success=False,
            message="Validation failed",
            expense_id=None,
            errors=["Amount must be positive"],
        )
        assert response.success is False
        assert response.expense_id is None
        assert response.errors is not None
        assert len(response.errors) == 1

    def test_create_expense_defaults(self):
        request = CreateExpense(text="Spent $50 at Starbucks")
        assert request.text == "Spent $50 at Starbucks"
        assert request.currency == "USD"
        assert request.amount is None
        assert request.category is None

    def test_create_expense_with_values(self):
        request = CreateExpense(
            text="Coffee purchase",
            amount=5.50,
            category="Food",
            currency="EUR",
        )
        assert request.amount == 5.50
        assert request.currency == "EUR"

    def test_expense_update_one(self):
        update = ExpenseUpdateOne(
            update_fields={"amount": 100.0, "category": "Shopping"}
        )
        assert update.update_fields["amount"] == 100.0


class TestBudgetModels:
    def test_create_budget_valid(self):
        budget = CreateBudget(
            category="Food & Dining",
            amount=500.0,
            period=BudgetPeriod.MONTHLY,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert budget.amount == 500.0
        assert budget.currency == Currencies.USD
        assert budget.period == BudgetPeriod.MONTHLY

    def test_create_budget_with_description(self):
        budget = CreateBudget(
            category="Entertainment",
            amount=200.0,
            currency=Currencies.EUR,
            period=BudgetPeriod.WEEKLY,
            start_date="2024-01-01",
            end_date="2024-01-07",
            description="Weekly entertainment budget",
        )
        assert budget.description == "Weekly entertainment budget"
        assert budget.currency == Currencies.EUR

    def test_budget_update_one(self):
        update = BudgetUpdateOne(update_fields={"amount": 600.0})
        assert update.update_fields["amount"] == 600.0


class TestCollectionModels:
    def test_expenses_model_alias(self):
        expense = Expenses(
            _id="exp-123",
            user_id="test_user",
            amount=100.0,
            currency=Currencies.USD,
            category="Shopping",
            date="2024-01-15",
            created_at="2024-01-15T10:00:00",
        )
        assert expense.id == "exp-123"

    def test_expenses_model_dump_alias(self):
        expense = Expenses(
            _id="exp-123",
            user_id="test_user",
            amount=100.0,
            currency=Currencies.USD,
            category="Shopping",
            date="2024-01-15",
            created_at="2024-01-15T10:00:00",
        )
        dumped = expense.model_dump(by_alias=True)
        assert "_id" in dumped
        assert dumped["_id"] == "exp-123"

    def test_expenses_defaults(self):
        expense = Expenses(
            _id="exp-123",
            user_id="test_user",
            amount=100.0,
            currency=Currencies.USD,
            category="Shopping",
            date="2024-01-15",
            created_at="2024-01-15T10:00:00",
        )
        assert expense.deleted is False
        assert expense.tags == []
        assert expense.merchant is None
        assert expense.notes is None

    def test_budgets_model_alias(self):
        budget = Budgets(
            _id="budget-123",
            user_id="test_user",
            category="Food",
            amount=500.0,
            currency=Currencies.USD,
            period=BudgetPeriod.MONTHLY,
            start_date="2024-01-01",
            end_date="2024-01-31",
            created_at="2024-01-01",
        )
        assert budget.id == "budget-123"

    def test_budgets_model_dump_alias(self):
        budget = Budgets(
            _id="budget-123",
            user_id="test_user",
            category="Food",
            amount=500.0,
            currency=Currencies.USD,
            period=BudgetPeriod.MONTHLY,
            start_date="2024-01-01",
            end_date="2024-01-31",
            created_at="2024-01-01",
        )
        dumped = budget.model_dump(by_alias=True)
        assert "_id" in dumped
        assert dumped["_id"] == "budget-123"


class TestExpenseTools:
    @pytest.mark.asyncio
    async def test_list_expenses_empty(self):
        with patch(
            "app.tools.expense_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = []
            from app.tools.expense_tools import list_expenses

            result = await list_expenses(user_id="test_user")
            assert result == []
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_expenses_with_data(self):
        mock_expense = {
            "_id": "exp-1",
            "user_id": "test_user",
            "amount": 50.0,
            "currency": "USD",
            "category": "Food",
            "date": "2024-01-15",
            "created_at": "2024-01-15",
            "deleted": False,
        }
        with patch(
            "app.tools.expense_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = [mock_expense]
            from app.tools.expense_tools import list_expenses

            result = await list_expenses(user_id="test_user")
            assert len(result) == 1
            assert result[0].amount == 50.0
            assert result[0].id == "exp-1"

    @pytest.mark.asyncio
    async def test_list_expenses_with_filters(self):
        mock_expense = {
            "_id": "exp-1",
            "user_id": "test_user",
            "amount": 50.0,
            "currency": "USD",
            "category": "Food",
            "date": "2024-01-15",
            "created_at": "2024-01-15",
            "deleted": False,
        }
        with patch(
            "app.tools.expense_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = [mock_expense]
            from app.tools.expense_tools import list_expenses

            result = await list_expenses(
                user_id="test_user",
                start_date="2024-01-01",
                end_date="2024-01-31",
                category="Food",
                min_amount=10,
                max_amount=100,
            )
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_individual_expense_not_found(self):
        with patch(
            "app.tools.expense_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = []
            from app.tools.expense_tools import list_individual_expense

            result = await list_individual_expense(
                user_id="test_user", expense_id="nonexistent"
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_list_individual_expense_found(self):
        mock_expense = {
            "_id": "exp-1",
            "user_id": "test_user",
            "amount": 50.0,
            "currency": "USD",
            "category": "Food",
            "date": "2024-01-15",
            "created_at": "2024-01-15",
            "deleted": False,
        }
        with patch(
            "app.tools.expense_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = [mock_expense]
            from app.tools.expense_tools import list_individual_expense

            result = await list_individual_expense(
                user_id="test_user", expense_id="exp-1"
            )
            assert result is not None
            assert result.id == "exp-1"
            assert result.amount == 50.0

    @pytest.mark.asyncio
    async def test_add_expense_empty_text(self):
        from app.tools.expense_tools import add_expense

        result = await add_expense(user_id="test_user", text="")
        assert result.success is False
        assert "No Text Provided" in result.message

    @pytest.mark.asyncio
    async def test_add_expense_whitespace_text(self):
        from app.tools.expense_tools import add_expense

        result = await add_expense(user_id="test_user", text="   ")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_update_expense_success(self):
        mock_result = MagicMock()
        mock_result.acknowledged = True
        mock_result.matched_count = 1
        mock_result.modified_count = 1
        with patch(
            "app.tools.expense_tools.update_one", new_callable=AsyncMock
        ) as mock_update:
            mock_update.return_value = mock_result
            from app.tools.expense_tools import update_expense

            result = await update_expense(
                user_id="test_user",
                expense_id="exp-1",
                update_fields={"amount": 100.0},
            )
            assert result.acknowledged is True
            assert result.modified_count == 1

    @pytest.mark.asyncio
    async def test_delete_expense_success(self):
        mock_result = MagicMock()
        mock_result.acknowledged = True
        mock_result.matched_count = 1
        mock_result.modified_count = 1
        with patch(
            "app.tools.expense_tools.update_one", new_callable=AsyncMock
        ) as mock_update:
            mock_update.return_value = mock_result
            from app.tools.expense_tools import delete_expense

            result = await delete_expense(user_id="test_user", expense_id="exp-1")
            assert result.acknowledged is True


class TestBudgetTools:
    @pytest.mark.asyncio
    async def test_get_all_user_budgets_empty(self):
        with patch(
            "app.tools.budget_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = []
            from app.tools.budget_tools import get_all_user_budgets

            result = await get_all_user_budgets(user_id="test_user")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_all_user_budgets_with_data(self):
        mock_budget = {
            "_id": "budget-1",
            "user_id": "test_user",
            "category": "Food",
            "amount": 500.0,
            "currency": "USD",
            "period": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "created_at": "2024-01-01",
            "deleted": False,
        }
        with patch(
            "app.tools.budget_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = [mock_budget]
            from app.tools.budget_tools import get_all_user_budgets

            result = await get_all_user_budgets(user_id="test_user")
            assert len(result) == 1
            assert result[0].category == "Food"

    @pytest.mark.asyncio
    async def test_create_budget_success(self):
        mock_result = MagicMock()
        mock_result.acknowledged = True
        mock_result.inserted_id = "budget-1"
        budget = Budgets(
            _id="budget-1",
            user_id="test_user",
            category="Food",
            amount=500.0,
            currency=Currencies.USD,
            period=BudgetPeriod.MONTHLY,
            start_date="2024-01-01",
            end_date="2024-01-31",
            created_at="2024-01-01",
        )
        with patch(
            "app.tools.budget_tools.insert_one", new_callable=AsyncMock
        ) as mock_insert:
            mock_insert.return_value = mock_result
            from app.tools.budget_tools import create_budget

            result = await create_budget(budget_data=budget)
            assert result.acknowledged is True

    @pytest.mark.asyncio
    async def test_update_budget_success(self):
        mock_result = MagicMock()
        mock_result.acknowledged = True
        mock_result.modified_count = 1
        with patch(
            "app.tools.budget_tools.update_one", new_callable=AsyncMock
        ) as mock_update:
            mock_update.return_value = mock_result
            from app.tools.budget_tools import update_budget

            result = await update_budget(
                user_id="test_user",
                budget_id="budget-1",
                update_fields={"amount": 600.0},
            )
            assert result.modified_count == 1

    @pytest.mark.asyncio
    async def test_delete_budget_success(self):
        mock_result = MagicMock()
        mock_result.acknowledged = True
        mock_result.modified_count = 1
        with patch(
            "app.tools.budget_tools.update_one", new_callable=AsyncMock
        ) as mock_update:
            mock_update.return_value = mock_result
            from app.tools.budget_tools import delete_budget

            result = await delete_budget(user_id="test_user", budget_id="budget-1")
            assert result.modified_count == 1

    @pytest.mark.asyncio
    async def test_get_budget_status_no_budgets(self):
        with patch(
            "app.tools.budget_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = []
            from app.tools.budget_tools import get_budget_status

            result = await get_budget_status(user_id="test_user")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_budget_status_under_budget(self):
        mock_budget = {
            "_id": "budget-1",
            "user_id": "test_user",
            "category": "Food",
            "amount": 500.0,
            "currency": "USD",
            "period": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "created_at": "2024-01-01",
            "deleted": False,
        }
        mock_expense_total = [{"_id": None, "total_spent": 200.0}]
        with patch(
            "app.tools.budget_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.side_effect = [[mock_budget], mock_expense_total]
            from app.tools.budget_tools import get_budget_status

            result = await get_budget_status(user_id="test_user")
            assert len(result) == 1
            assert result[0]["spent"] == 200.0
            assert result[0]["remaining"] == 300.0
            assert result[0]["utilization"] == 40.0
            assert result[0]["warning"] is False
            assert result[0]["exceeded"] is False

    @pytest.mark.asyncio
    async def test_get_budget_status_warning(self):
        mock_budget = {
            "_id": "budget-1",
            "user_id": "test_user",
            "category": "Food",
            "amount": 500.0,
            "currency": "USD",
            "period": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "created_at": "2024-01-01",
            "deleted": False,
        }
        mock_expense_total = [{"_id": None, "total_spent": 450.0}]
        with patch(
            "app.tools.budget_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.side_effect = [[mock_budget], mock_expense_total]
            from app.tools.budget_tools import get_budget_status

            result = await get_budget_status(user_id="test_user")
            assert result[0]["utilization"] == 90.0
            assert result[0]["warning"] is True
            assert result[0]["exceeded"] is False

    @pytest.mark.asyncio
    async def test_get_budget_status_exceeded(self):
        mock_budget = {
            "_id": "budget-1",
            "user_id": "test_user",
            "category": "Food",
            "amount": 500.0,
            "currency": "USD",
            "period": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "created_at": "2024-01-01",
            "deleted": False,
        }
        mock_expense_total = [{"_id": None, "total_spent": 600.0}]
        with patch(
            "app.tools.budget_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.side_effect = [[mock_budget], mock_expense_total]
            from app.tools.budget_tools import get_budget_status

            result = await get_budget_status(user_id="test_user")
            assert result[0]["utilization"] == 120.0
            assert result[0]["warning"] is True
            assert result[0]["exceeded"] is True

    @pytest.mark.asyncio
    async def test_get_budget_status_no_expenses(self):
        mock_budget = {
            "_id": "budget-1",
            "user_id": "test_user",
            "category": "Food",
            "amount": 500.0,
            "currency": "USD",
            "period": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "created_at": "2024-01-01",
            "deleted": False,
        }
        with patch(
            "app.tools.budget_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.side_effect = [[mock_budget], []]
            from app.tools.budget_tools import get_budget_status

            result = await get_budget_status(user_id="test_user")
            assert result[0]["spent"] == 0
            assert result[0]["remaining"] == 500.0


class TestAnalyticsTools:
    @pytest.mark.asyncio
    async def test_analyze_spendings_empty(self):
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = []
            from app.tools.analytics_tools import analyze_spendings

            result = await analyze_spendings(user_id="test_user")
            assert result == []

    @pytest.mark.asyncio
    async def test_analyze_spendings_with_data(self):
        mock_result = [
            {"_id": "Food", "total": 500.0, "count": 10},
            {"_id": "Transport", "total": 200.0, "count": 5},
        ]
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = mock_result
            from app.tools.analytics_tools import analyze_spendings

            result = await analyze_spendings(user_id="test_user")
            assert len(result) == 2
            assert result[0]["percentage"] > 0
            total_percentage = sum(item["percentage"] for item in result)
            assert total_percentage == 100.0

    @pytest.mark.asyncio
    async def test_analyze_spendings_with_dates(self):
        mock_result = [{"_id": "Food", "total": 100.0, "count": 2}]
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = mock_result
            from app.tools.analytics_tools import analyze_spendings

            result = await analyze_spendings(
                user_id="test_user",
                start_date="2024-01-01",
                end_date="2024-01-31",
            )
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_top_merchants_empty(self):
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = []
            from app.tools.analytics_tools import get_top_merchants

            result = await get_top_merchants(user_id="test_user")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_top_merchants_with_data(self):
        mock_result = [
            {"_id": "Starbucks", "total": 200.0, "count": 20},
            {"_id": "Amazon", "total": 150.0, "count": 5},
        ]
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = mock_result
            from app.tools.analytics_tools import get_top_merchants

            result = await get_top_merchants(user_id="test_user", limit=5)
            assert len(result) == 2
            assert result[0]["_id"] == "Starbucks"

    @pytest.mark.asyncio
    async def test_get_spending_trends_empty(self):
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = []
            from app.tools.analytics_tools import get_spending_trends

            result = await get_spending_trends(user_id="test_user")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_spending_trends_with_data(self):
        mock_result = [
            {"_id": {"year": 2024, "month": 1}, "total": 1000.0, "count": 20},
            {"_id": {"year": 2024, "month": 2}, "total": 800.0, "count": 15},
        ]
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = mock_result
            from app.tools.analytics_tools import get_spending_trends

            result = await get_spending_trends(user_id="test_user")
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_average_spending_empty(self):
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = []
            from app.tools.analytics_tools import get_average_spending

            result = await get_average_spending(user_id="test_user")
            assert result["average"] == 0
            assert result["periods_count"] == 0

    @pytest.mark.asyncio
    async def test_get_average_spending_yearly(self):
        mock_result = [{"_id": None, "average": 12000.0, "periods_count": 2}]
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = mock_result
            from app.tools.analytics_tools import get_average_spending

            result = await get_average_spending(
                user_id="test_user", period=BudgetPeriod.YEARLY
            )
            assert result["average"] == 12000.0
            assert result["periods_count"] == 2

    @pytest.mark.asyncio
    async def test_get_average_spending_monthly(self):
        mock_result = [{"_id": None, "average": 1500.0, "periods_count": 6}]
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = mock_result
            from app.tools.analytics_tools import get_average_spending

            result = await get_average_spending(
                user_id="test_user", period=BudgetPeriod.MONTHLY
            )
            assert result["average"] == 1500.0

    @pytest.mark.asyncio
    async def test_get_average_spending_weekly(self):
        mock_result = [{"_id": None, "average": 350.0, "periods_count": 12}]
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = mock_result
            from app.tools.analytics_tools import get_average_spending

            result = await get_average_spending(
                user_id="test_user", period=BudgetPeriod.WEEKLY
            )
            assert result["average"] == 350.0

    @pytest.mark.asyncio
    async def test_get_average_spending_daily(self):
        mock_result = [{"_id": None, "average": 50.0, "periods_count": 30}]
        with patch(
            "app.tools.analytics_tools.query_read", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = mock_result
            from app.tools.analytics_tools import get_average_spending

            result = await get_average_spending(
                user_id="test_user", period=BudgetPeriod.DAILY
            )
            assert result["average"] == 50.0


class TestLLMService:
    def test_llm_service_no_api_key(self):
        with patch("app.services.llm_services.config") as mock_config:
            mock_config.ANTHROPIC_API_KEY = None
            from app.services.llm_services import LLMService

            service = LLMService()
            assert service.agent is None

    def test_llm_service_with_api_key(self):
        with patch("app.services.llm_services.config") as mock_config:
            mock_config.ANTHROPIC_API_KEY = "test-api-key"
            mock_config.DATABASE_NAME = "test_db"
            mock_config.MONGO_URI = "mongodb://localhost"
            with patch("app.services.llm_services.ChatAnthropic"):
                from app.services.llm_services import LLMService

                service = LLMService()
                assert service.agent is not None

    @pytest.mark.asyncio
    async def test_chat_without_agent_raises(self):
        with patch("app.services.llm_services.config") as mock_config:
            mock_config.ANTHROPIC_API_KEY = None
            from app.services.llm_services import LLMService

            service = LLMService()
            with pytest.raises(RuntimeError, match="LLM service not initialized"):
                await service.chat("test", "prompt")

    @pytest.mark.asyncio
    async def test_parse_structured_without_agent_raises(self):
        with patch("app.services.llm_services.config") as mock_config:
            mock_config.ANTHROPIC_API_KEY = None
            from app.services.llm_services import LLMService

            service = LLMService()
            with pytest.raises(RuntimeError, match="LLM service not initialized"):
                await service.parse_structured("test", "prompt", ExpenseExtraction)


class TestAgent:
    @pytest.mark.asyncio
    async def test_parse_expense_success(self):
        mock_response = ExpenseExtraction(
            user_id="test_user",
            amount=50.0,
            currency=Currencies.USD,
            merchant="Starbucks",
            category="Food & Dining",
            date="2024-01-15",
        )
        with patch("app.agents.agent.LLMService") as MockLLMService:
            mock_service = MockLLMService.return_value
            mock_service.parse_structured = AsyncMock(return_value=mock_response)
            from app.agents.agent import Agent

            agent = Agent()
            result = await agent.parse_expense(
                user_prompt="Spent $50 at Starbucks",
                user_id="test_user",
            )
            assert result.amount == 50.0
            assert result.merchant == "Starbucks"

    @pytest.mark.asyncio
    async def test_process_expense_valid(self):
        parsed_data = ExpenseExtraction(
            user_id="test_user",
            amount=50.0,
            currency=Currencies.USD,
            merchant="Starbucks",
            category="Food & Dining",
            date="2024-01-15",
        )
        mock_validation = ExpenseValidation(
            is_valid=True,
            errors=[],
            warnings=[],
        )
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(acknowledged=True)
        )
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)

        with patch("app.agents.agent.LLMService") as MockLLMService:
            mock_service = MockLLMService.return_value
            mock_service.parse_structured = AsyncMock(return_value=mock_validation)
            with patch("app.agents.agent.Database") as MockDatabase:
                MockDatabase.get_database.return_value = mock_db
                from app.agents.agent import Agent

                agent = Agent()
                result = await agent.process_expense(parsed_data=parsed_data)
                assert result.success is True

    @pytest.mark.asyncio
    async def test_process_expense_invalid(self):
        parsed_data = ExpenseExtraction(
            user_id="test_user",
            amount=50.0,
            currency=Currencies.USD,
            merchant="Starbucks",
            category="Food & Dining",
            date="2024-01-15",
        )
        mock_validation = ExpenseValidation(
            is_valid=False,
            errors=["Invalid date"],
            warnings=[],
        )
        with patch("app.agents.agent.LLMService") as MockLLMService:
            mock_service = MockLLMService.return_value
            mock_service.parse_structured = AsyncMock(return_value=mock_validation)
            from app.agents.agent import Agent

            agent = Agent()
            result = await agent.process_expense(parsed_data=parsed_data)
            assert result.success is False
            assert result.errors is not None
            assert "Invalid date" in result.errors

    @pytest.mark.asyncio
    async def test_process_expense_no_db(self):
        parsed_data = ExpenseExtraction(
            user_id="test_user",
            amount=50.0,
            currency=Currencies.USD,
            merchant="Starbucks",
            category="Food & Dining",
            date="2024-01-15",
        )
        mock_validation = ExpenseValidation(
            is_valid=True,
            errors=[],
            warnings=[],
        )
        with patch("app.agents.agent.LLMService") as MockLLMService:
            mock_service = MockLLMService.return_value
            mock_service.parse_structured = AsyncMock(return_value=mock_validation)
            with patch("app.agents.agent.Database") as MockDatabase:
                MockDatabase.get_database.return_value = None
                from app.agents.agent import Agent

                agent = Agent()
                result = await agent.process_expense(parsed_data=parsed_data)
                assert result.success is False
                assert "Lack of DB Connection" in result.message


class TestDateHandling:
    def test_date_format_consistency(self):
        from datetime import datetime, timezone

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        assert len(date_str) == 10
        assert date_str[4] == "-"
        assert date_str[7] == "-"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
