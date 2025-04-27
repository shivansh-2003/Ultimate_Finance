# models/schemas.py
from typing import List, Dict, Optional, Union, Any, Literal
from enum import Enum
from datetime import datetime, date
from pydantic import BaseModel, Field, validator, root_validator
from uuid import UUID, uuid4

class FrequencyType(str, Enum):
    """Enumeration of transaction frequency types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    ONCE = "once"
    IRREGULAR = "irregular"

class CategoryType(str, Enum):
    """Enumeration of category types."""
    ESSENTIAL = "essential"
    DISCRETIONARY = "discretionary"
    SAVINGS = "savings"
    DEBT = "debt"
    INCOME = "income"
    OTHER = "other"

class TransactionType(str, Enum):
    """Enumeration of transaction types."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"

class UserPreference(BaseModel):
    """User preferences for budget planning."""
    currency: str = "USD"
    date_format: str = "YYYY-MM-DD"
    savings_goal_percentage: float = 20.0  # Percentage of income to save
    emergency_fund_target: float = 10000.0  # Target emergency fund amount
    risk_tolerance: Literal["low", "medium", "high"] = "medium"
    budget_categories_visibility: Dict[str, bool] = Field(default_factory=dict)
    preferred_analysis_timeframe: Literal["weekly", "monthly", "quarterly", "annually"] = "monthly"

class Category(BaseModel):
    """Financial category model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    type: CategoryType
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "8f9d2e3c-1a5b-4f6d-8e7c-9a0b1c2d3e4f",
                "name": "Groceries",
                "type": "essential",
                "description": "Food and household items",
                "keywords": ["grocery", "supermarket", "food"],
                "parent_id": "5a6b7c8d-9e0f-1a2b-3c4d-5e6f7a8b9c0d",  # Food category ID
                "icon": "shopping-cart",
                "color": "#4CAF50"
            }
        }

class IncomeSource(BaseModel):
    """Income source model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    amount: float
    frequency: FrequencyType
    description: Optional[str] = None
    category_id: Optional[str] = None
    is_active: bool = True
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Income amount must be positive')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
                "name": "Salary",
                "amount": 5000.00,
                "frequency": "monthly",
                "description": "Main job salary",
                "category_id": "income-category-id",
                "is_active": True,
                "start_date": "2023-01-01",
                "end_date": None
            }
        }

class Expense(BaseModel):
    """Expense model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    amount: float
    frequency: FrequencyType
    category_id: str
    description: Optional[str] = None
    is_fixed: bool = False  # True for fixed expenses (rent, subscription)
    due_date: Optional[int] = None  # Day of month for monthly expenses
    is_active: bool = True
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Expense amount must be positive')
        return v
    
    @validator('due_date')
    def validate_due_date(cls, v):
        if v is not None and (v < 1 or v > 31):
            raise ValueError('Due date must be between 1 and 31')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e",
                "name": "Rent",
                "amount": 1200.00,
                "frequency": "monthly",
                "category_id": "housing-category-id",
                "description": "Apartment rent",
                "is_fixed": True,
                "due_date": 1,  # Due on 1st of month
                "is_active": True,
                "start_date": "2023-01-01",
                "end_date": None
            }
        }

class Transaction(BaseModel):
    """Transaction model representing actual financial transactions."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    date: date
    amount: float  # Positive for income, negative for expenses
    description: str
    category_id: Optional[str] = None
    transaction_type: TransactionType
    account_id: Optional[str] = None
    merchant: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    is_recurring: bool = False
    is_cleared: bool = False  # Whether transaction has cleared account
    attachment_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
                "date": "2023-02-15",
                "amount": -125.45,
                "description": "Walmart Grocery",
                "category_id": "groceries-category-id",
                "transaction_type": "expense",
                "account_id": "checking-account-id",
                "merchant": "Walmart",
                "tags": ["essentials", "food"],
                "notes": "Weekly grocery shopping",
                "is_recurring": False,
                "is_cleared": True,
                "attachment_url": None
            }
        }

class Account(BaseModel):
    """Financial account model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    type: Literal["checking", "savings", "credit", "investment", "cash", "other"]
    balance: float = 0.0
    currency: str = "USD"
    is_active: bool = True
    include_in_budget: bool = True
    notes: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a",
                "name": "Primary Checking",
                "type": "checking",
                "balance": 3500.75,
                "currency": "USD",
                "is_active": True,
                "include_in_budget": True,
                "notes": "Main account for daily expenses",
                "last_updated": "2023-02-20T15:30:45.123Z"
            }
        }

class Budget(BaseModel):
    """Budget model with planned income and expenses."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    start_date: date
    end_date: date
    income_sources: List[IncomeSource] = Field(default_factory=list)
    expenses: List[Expense] = Field(default_factory=list)
    savings_goal: float = 0.0
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @root_validator
    def validate_dates(cls, values):
        start = values.get('start_date')
        end = values.get('end_date')
        if start and end and start > end:
            raise ValueError('End date must be after start date')
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "id": "5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b",
                "name": "February 2023 Budget",
                "start_date": "2023-02-01",
                "end_date": "2023-02-28",
                "income_sources": [],  # List of IncomeSource objects
                "expenses": [],  # List of Expense objects
                "savings_goal": 1000.00,
                "notes": "Saving for summer vacation",
                "created_at": "2023-01-25T12:00:00Z",
                "updated_at": "2023-01-25T12:00:00Z"
            }
        }

class SavingsGoal(BaseModel):
    """Savings goal model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    target_amount: float
    current_amount: float = 0.0
    target_date: Optional[date] = None
    priority: Literal["low", "medium", "high"] = "medium"
    category: Optional[str] = None  # E.g., "Emergency Fund", "Vacation", etc.
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('target_amount', 'current_amount')
    def amount_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Amount must be positive')
        return v
    
    @property
    def progress_percentage(self) -> float:
        """Calculate the savings goal progress as a percentage."""
        if self.target_amount <= 0:
            return 0
        return min(100.0, (self.current_amount / self.target_amount) * 100)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "6f7a8b9c-0d1e-2f3a-4b5c-6d7e8f9a0b1c",
                "name": "Emergency Fund",
                "target_amount": 10000.00,
                "current_amount": 3500.00,
                "target_date": "2023-12-31",
                "priority": "high",
                "category": "Emergency Fund",
                "notes": "Three months of expenses",
                "is_active": True,
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2023-02-15T14:30:00Z"
            }
        }

class BudgetAnalysis(BaseModel):
    """Budget analysis result model."""
    period_start: date
    period_end: date
    total_income: float = 0.0
    total_expenses: float = 0.0
    net_cash_flow: float = 0.0
    expense_by_category: Dict[str, float] = Field(default_factory=dict)
    income_by_source: Dict[str, float] = Field(default_factory=dict)
    savings_rate: float = 0.0
    budget_adherence: Dict[str, float] = Field(default_factory=dict)  # Planned vs actual by category
    optimization_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    
    @root_validator
    def calculate_derived_fields(cls, values):
        income = values.get('total_income', 0)
        expenses = values.get('total_expenses', 0)
        
        # Calculate net cash flow
        values['net_cash_flow'] = income - expenses
        
        # Calculate savings rate
        if income > 0:
            values['savings_rate'] = ((income - expenses) / income) * 100
        else:
            values['savings_rate'] = 0
            
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "period_start": "2023-02-01",
                "period_end": "2023-02-28",
                "total_income": 5000.00,
                "total_expenses": 3500.00,
                "net_cash_flow": 1500.00,
                "expense_by_category": {
                    "Housing": 1200.00,
                    "Food": 800.00,
                    "Transportation": 300.00,
                    "Entertainment": 200.00,
                    "Utilities": 350.00,
                    "Other": 650.00
                },
                "income_by_source": {
                    "Salary": 4800.00,
                    "Side Gig": 200.00
                },
                "savings_rate": 30.0,
                "budget_adherence": {
                    "Housing": 100.0,  # 100% means actual = planned
                    "Food": 110.0,     # 110% means spent 10% more than planned
                    "Entertainment": 80.0  # 80% means spent 20% less than planned
                },
                "optimization_suggestions": [
                    {
                        "category": "Food",
                        "message": "Your food expenses are somewhat higher than recommended.",
                        "potential_savings": 100.00,
                        "urgency": "medium"
                    }
                ]
            }
        }

class BudgetRequest(BaseModel):
    """Request model for budget analysis."""
    user_input: str
    transactions: Optional[List[Transaction]] = None
    income_sources: Optional[List[IncomeSource]] = None
    expenses: Optional[List[Expense]] = None
    timeframe: Literal["weekly", "monthly", "quarterly", "annually"] = "monthly"
    
    class Config:
        schema_extra = {
            "example": {
                "user_input": "I want to create a budget for next month. I make $5000 a month from my job, and my main expenses are $1200 for rent, $400 for car payment, and about $600 for groceries.",
                "transactions": [],  # Optional list of past transactions
                "income_sources": [],  # Optional list of income sources
                "expenses": [],  # Optional list of expenses
                "timeframe": "monthly"
            }
        }

class BudgetResponse(BaseModel):
    """Response model from budget agent."""
    budget_analysis: Optional[BudgetAnalysis] = None
    recommendations: str
    suggested_budget: Optional[Budget] = None
    savings_recommendations: Optional[Dict[str, Any]] = None
    visual_data: Optional[Dict[str, Any]] = None  # Data for visualizations
    
    class Config:
        schema_extra = {
            "example": {
                "budget_analysis": {},  # BudgetAnalysis object
                "recommendations": "Based on your financial situation, I recommend reducing your food expenses by meal planning and cooking at home more often. This could save you approximately $100 per month.",
                "suggested_budget": {},  # Budget object
                "savings_recommendations": {
                    "emergency_fund": 500.00,
                    "retirement": 300.00,
                    "short_term_goals": 200.00
                },
                "visual_data": {
                    "expense_breakdown": {
                        "labels": ["Housing", "Food", "Transportation", "Entertainment", "Utilities", "Other"],
                        "values": [1200, 800, 300, 200, 350, 650]
                    },
                    "monthly_cashflow": {
                        "labels": ["Income", "Expenses", "Savings"],
                        "values": [5000, 3500, 1500]
                    }
                }
            }
        }

class UserSession(BaseModel):
    """User session data for maintaining context between interactions."""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_budget: Optional[Budget] = None
    extracted_financial_data: Dict[str, Any] = Field(default_factory=dict)
    last_analysis: Optional[BudgetAnalysis] = None
    active_goals: List[SavingsGoal] = Field(default_factory=list)
    preferences: UserPreference = Field(default_factory=UserPreference)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
                "user_id": "user-123",
                "conversation_history": [
                    {"role": "user", "content": "I want to create a budget."},
                    {"role": "assistant", "content": "Great! Let's start by understanding your income and expenses."}
                ],
                "current_budget": None,  # Budget object
                "extracted_financial_data": {
                    "income": [{"source": "Salary", "amount": 5000, "frequency": "monthly"}],
                    "expenses": [{"name": "Rent", "amount": 1200, "frequency": "monthly"}]
                },
                "last_analysis": None,  # BudgetAnalysis object
                "active_goals": [],  # List of SavingsGoal objects
                "preferences": {
                    "currency": "USD",
                    "date_format": "YYYY-MM-DD",
                    "savings_goal_percentage": 20.0
                },
                "created_at": "2023-02-20T10:00:00Z",
                "last_updated": "2023-02-20T10:15:00Z"
            }
        }