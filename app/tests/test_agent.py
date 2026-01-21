"""
Comprehensive tests for Personal Finance Intelligence Agent

Run with: pytest app/tests/test_agent.py -v
"""

import pytest
from unittest.mock import AsyncMock, patch

# Models
from app.models.agent import ExpenseExtraction, ExpenseValidation, ExpenseResponse
from app.models.collections import Expenses, Budgets
from app.models.expenses import CreateExpense, UpdateOne as ExpenseUpdateOne
from app.models.budgets import CreateBudget, UpdateOne as BudgetUpdateOne
from app.utils.enums import Currencies, BudgetPeriod

class TestExpenseModels:
    """Test expense-related Pydantic models"""

    def test_expense_extraction_valid(self):
        """Test valid ExpenseExtraction creation"""
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

    def test_expense_extraction_defaults(self):
        """Test default values"""
        expense = ExpenseExtraction(
            user_id="test_user",
            amount=25.0,
            category="Other",
            date="2024-01-15",
        )
        assert expense.currency == Currencies.USD
        assert expense.merchant is None

    def test_expense_response_success(self):
        """Test successful ExpenseResponse"""
        response = ExpenseResponse(
            success=True,
            message="Expense added",
            expense_id="abc-123",
        )
        assert response.success is True
        assert response.expense_id == "abc-123"

    def test_expense_response_failure(self):
        """Test failed ExpenseResponse with errors"""
        response = ExpenseResponse(
            success=False,
            message="Validation failed",
            expense_id=None,
            errors=["Amount must be positive"],
        )
        assert response.success is False

    def test_create_expense_request(self):
        """Test CreateExpense request model"""
        request = CreateExpense(
            text="Spent $50 at Starbucks yesterday",
            amount=50.0,
            category="Food",
        )
        assert request.text == "Spent $50 at Starbucks yesterday"
        assert request.currency == "USD"  # default


class TestBudgetModels:
    """Test budget-related Pydantic models"""

    def test_budget_model_valid(self):
        """Test valid Budgets creation"""
        budget = Budgets(
            _id="budget-123",
            user_id="test_user",
            category="Food & Dining",
            amount=500.0,
            currency=Currencies.USD,
            period=BudgetPeriod.MONTHLY,
            start_date="2024-01-01",
            end_date="2024-01-31",
            created_at="2024-01-01",
        )
        assert budget.id == "budget-123"
        assert budget.amount == 500.0

    def test_create_budget_request(self):
        """Test CreateBudget request model"""
        request = CreateBudget(
            category="Food & Dining",
            amount=500.0,
            period=BudgetPeriod.MONTHLY,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert request.currency == Currencies.USD  # default


class TestExpensesCollectionModel:
    """Test Expenses collection model"""

    def test_expenses_model_alias(self):
        """Test _id alias works correctly"""
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

        # Test model_dump with alias
        dumped = expense.model_dump(by_alias=True)
        assert "_id" in dumped
        assert dumped["_id"] == "exp-123"


# ============================================================================
# TOOL TESTS (with mocked database)
# ============================================================================

class TestExpenseTools:
    """Test expense tools with mocked dependencies"""

    @pytest.mark.asyncio
    async def test_list_expenses_empty(self):
        """Test list_expenses returns empty list when no expenses"""
        with patch("app.tools.expense_tools.query_read", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = []

            from app.tools.expense_tools import list_expenses
            result = await list_expenses(user_id="test_user")

            assert result == []
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_expenses_with_filters(self):
        """Test list_expenses with date and category filters"""
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

        with patch("app.tools.expense_tools.query_read", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [mock_expense]

            from app.tools.expense_tools import list_expenses
            result = await list_expenses(
                user_id="test_user",
                start_date="2024-01-01",
                end_date="2024-01-31",
                category="Food",
            )

            assert len(result) == 1
            assert result[0].amount == 50.0

    @pytest.mark.asyncio
    async def test_list_individual_expense_not_found(self):
        """Test list_individual_expense returns None when not found"""
        with patch("app.tools.expense_tools.query_read", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = []

            from app.tools.expense_tools import list_individual_expense
            result = await list_individual_expense(
                user_id="test_user",
                expense_id="non-existent"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_list_individual_expense_found(self):
        """Test list_individual_expense returns expense when found"""
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

        with patch("app.tools.expense_tools.query_read", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [mock_expense]

            from app.tools.expense_tools import list_individual_expense
            result = await list_individual_expense(
                user_id="test_user",
                expense_id="exp-1"
            )

            assert result is not None
            assert result.id == "exp-1"


class TestAnalyticsTools:
    """Test analytics tools with mocked database"""

    @pytest.mark.asyncio
    async def test_analyze_spendings(self):
        """Test analyze_spendings aggregation"""
        mock_result = [
            {"_id": "Food", "total": 500.0, "count": 10},
            {"_id": "Transport", "total": 200.0, "count": 5},
        ]

        with patch("app.tools.analytics_tools.query_read", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_result

            from app.tools.analytics_tools import analyze_spendings
            result = await analyze_spendings(user_id="test_user")

            assert len(result) == 2
            assert result[0]["percentage"] > 0

    @pytest.mark.asyncio
    async def test_get_average_spending_monthly(self):
        """Test get_average_spending with monthly period"""
        mock_result = [{"_id": None, "average": 1500.0, "periods_count": 6}]

        with patch("app.tools.analytics_tools.query_read", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = mock_result

            from app.tools.analytics_tools import get_average_spending
            result = await get_average_spending(
                user_id="test_user",
                period=BudgetPeriod.MONTHLY
            )

            assert result["average"] == 1500.0
            assert result["periods_count"] == 6

    @pytest.mark.asyncio
    async def test_get_average_spending_empty(self):
        """Test get_average_spending with no data"""
        with patch("app.tools.analytics_tools.query_read", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = []

            from app.tools.analytics_tools import get_average_spending
            result = await get_average_spending(user_id="test_user")

            assert result["average"] == 0
            assert result["periods_count"] == 0


class TestBudgetTools:
    """Test budget tools with mocked database"""

    @pytest.mark.asyncio
    async def test_get_all_user_budgets(self):
        """Test retrieving user budgets"""
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

        with patch("app.tools.budget_tools.query_read", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [mock_budget]

            from app.tools.budget_tools import get_all_user_budgets
            result = await get_all_user_budgets(user_id="test_user")

            assert len(result) == 1
            assert result[0].category == "Food"

    @pytest.mark.asyncio
    async def test_get_budget_status(self):
        """Test budget status calculation"""
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
        mock_expense_total = [{"_id": None, "total_spent": 300.0}]

        with patch("app.tools.budget_tools.query_read", new_callable=AsyncMock) as mock_query:
            # First call returns budgets, second returns expense totals
            mock_query.side_effect = [[mock_budget], mock_expense_total]

            from app.tools.budget_tools import get_budget_status
            result = await get_budget_status(user_id="test_user")

            assert len(result) == 1
            assert result[0]["spent"] == 300.0
            assert result[0]["remaining"] == 200.0
            assert result[0]["utilization"] == 60.0
            assert result[0]["warning"] is False
            assert result[0]["exceeded"] is False


# ============================================================================
# LLM SERVICE TESTS
# ============================================================================

class TestLLMService:
    """Test LLM service initialization and methods"""

    def test_llm_service_no_api_key(self):
        """Test LLMService handles missing API key"""
        with patch("app.services.llm_services.config") as mock_config:
            mock_config.ANTHROPIC_API_KEY = None

            from app.services.llm_services import LLMService
            service = LLMService()

            assert service.agent is None

    @pytest.mark.asyncio
    async def test_chat_without_agent_raises(self):
        """Test chat raises error when agent not initialized"""
        with patch("app.services.llm_services.config") as mock_config:
            mock_config.ANTHROPIC_API_KEY = None

            from app.services.llm_services import LLMService
            service = LLMService()

            with pytest.raises(RuntimeError, match="LLM service not initialized"):
                await service.chat("test", "prompt")


# ============================================================================
# AGENT TESTS
# ============================================================================

class TestAgent:
    """Test Agent class methods"""

    @pytest.mark.asyncio
    async def test_parse_expense_success(self):
        """Test successful expense parsing"""
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
            mock_service.parse_structured = AsyncMock(return_value=mock_response.model_dump())

            from app.agents.agent import Agent
            agent = Agent()
            result = await agent.parse_expense(
                user_prompt="Spent $50 at Starbucks",
                user_id="test_user"
            )

            assert result.amount == 50.0
            assert result.merchant == "Starbucks"


# ============================================================================
# INTEGRATION TESTS (require running services)
# ============================================================================

class TestIntegration:
    """Integration tests - require MongoDB and API key"""

    @pytest.mark.skip(reason="Requires running MongoDB")
    @pytest.mark.asyncio
    async def test_full_expense_workflow(self):
        """Test complete expense creation workflow"""
        # This would test the full flow from API to database
        pass

    @pytest.mark.skip(reason="Requires running MongoDB")
    @pytest.mark.asyncio
    async def test_full_budget_workflow(self):
        """Test complete budget creation workflow"""
        pass


# ============================================================================
# UTILITY TESTS
# ============================================================================

class TestEnums:
    """Test enum values"""

    def test_currencies(self):
        """Test currency enum values"""
        assert Currencies.USD.value == "USD"
        assert Currencies.EUR.value == "EUR"
        assert Currencies.INR.value == "INR"

    def test_budget_periods(self):
        """Test budget period enum values"""
        assert BudgetPeriod.DAILY.value == "daily"
        assert BudgetPeriod.WEEKLY.value == "weekly"
        assert BudgetPeriod.MONTHLY.value == "monthly"
        assert BudgetPeriod.YEARLY.value == "yearly"


# ============================================================================
# DATE HANDLING TESTS
# ============================================================================

class TestDateHandling:
    """Test date formatting across the application"""

    def test_date_format_consistency(self):
        """Ensure date format is YYYY-MM-DD"""
        from datetime import datetime, timezone

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Should be exactly 10 characters: YYYY-MM-DD
        assert len(date_str) == 10
        assert date_str[4] == "-"
        assert date_str[7] == "-"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
