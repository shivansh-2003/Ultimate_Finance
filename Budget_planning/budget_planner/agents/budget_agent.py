# agent/budget_agent.py
from typing import Dict, List, Tuple, Any, Optional
from datetime import date
from langchain_anthropic import ChatAnthropic
from langchain.schema import Document
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# Import from other modules
from budget_planner.core.helper import parse_financial_data, format_currency
from budget_planner.utils.prompts import FINANCIAL_DATA_EXTRACTION_PROMPT, BUDGET_RECOMMENDATION_PROMPT
from budget_planner.core.helper import calculate_monthly_equivalent, analyze_expense_ratio, suggest_savings_allocation
from budget_planner.utils.config import settings
from budget_planner.models.schema import (
    BudgetAnalysis, BudgetRequest, BudgetResponse, Transaction, 
    IncomeSource, Expense, FrequencyType, CategoryType, Budget
)

# Define the state of our budget agent (integrating with schema models)
class BudgetAgentState(BaseModel):
    user_input: str
    income_sources: List[IncomeSource] = Field(default_factory=list)
    expenses: List[Expense] = Field(default_factory=list)
    transactions: List[Transaction] = Field(default_factory=list)
    budget_analysis: Optional[BudgetAnalysis] = None
    current_step: str = "intake"  # Possible values: intake, analyze, recommend
    working_memory: Dict[str, Any] = Field(default_factory=dict)
    response: Optional[str] = None

# Define the nodes in our graph
def intake_financial_data(state: BudgetAgentState) -> BudgetAgentState:
    """Process initial user input and extract financial information."""
    # Use LLM to extract income and expense information from user input
    
    llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL, api_key=settings.ANTHROPIC_API_KEY)
    response = llm.invoke(FINANCIAL_DATA_EXTRACTION_PROMPT.format(user_input=state.user_input))
    
    # Parse LLM response into structured data
    extracted_data = parse_financial_data(response.content)
    
    # Convert extracted data to proper schema models
    income_sources = []
    for income_data in extracted_data.get("income_data", []):
        try:
            income_sources.append(
                IncomeSource(
                    name=income_data.get("source", "Income"),
                    amount=float(income_data.get("amount", 0)),
                    frequency=income_data.get("frequency", "monthly"),
                    description=f"Extracted from user input: {state.user_input}"
                )
            )
        except Exception as e:
            # Handle validation errors
            continue
    
    expenses = []
    for expense_data in extracted_data.get("expense_data", []):
        try:
            expenses.append(
                Expense(
                    name=expense_data.get("description", "Expense"),
                    amount=float(expense_data.get("amount", 0)),
                    frequency=expense_data.get("frequency", "monthly"),
                    category_id=expense_data.get("category", "Other"),
                    description=f"Extracted from user input: {state.user_input}"
                )
            )
        except Exception as e:
            # Handle validation errors
            continue
    
    return BudgetAgentState(
        user_input=state.user_input,
        income_sources=income_sources,
        expenses=expenses,
        transactions=state.transactions,
        current_step="analyze",
        working_memory=state.working_memory,
    )

def analyze_budget(state: BudgetAgentState) -> BudgetAgentState:
    """Analyze income and expenses to create a budget analysis."""
    today = date.today()
    # Determine period start and end based on current month
    period_start = date(today.year, today.month, 1)
    
    # Simple way to get month end
    if today.month == 12:
        period_end = date(today.year + 1, 1, 1)
    else:
        period_end = date(today.year, today.month + 1, 1)
    period_end = date.fromordinal(period_end.toordinal() - 1)  # Last day of month
    
    # Normalize all values to monthly equivalents
    total_income = 0
    income_by_source = {}
    for income in state.income_sources:
        monthly_amount = calculate_monthly_equivalent(income.amount, income.frequency)
        total_income += monthly_amount
        income_by_source[income.name] = monthly_amount
    
    total_expenses = 0
    expense_by_category = {}
    
    for expense in state.expenses:
        monthly_amount = calculate_monthly_equivalent(expense.amount, expense.frequency)
        total_expenses += monthly_amount
        
        category = expense.category_id
        if category in expense_by_category:
            expense_by_category[category] += monthly_amount
        else:
            expense_by_category[category] = monthly_amount
    
    # Calculate net cash flow and other metrics
    net_cash_flow = total_income - total_expenses
    
    # Calculate expense ratios
    expense_ratios = analyze_expense_ratio(expense_by_category, total_income)
    
    # Suggest savings allocation if there's a positive cash flow
    savings_allocation = suggest_savings_allocation(net_cash_flow)
    
    # Generate optimization suggestions
    optimization_suggestions = []
    for category, amount in expense_by_category.items():
        ratio = expense_ratios.get(category, 0)
        
        # Simple rules for suggestions
        if category == "Housing" and ratio > 35:
            optimization_suggestions.append({
                "category": category,
                "message": f"Your housing expenses are {ratio:.1f}% of your income, which is above the recommended 30-35%.",
                "potential_savings": amount - (total_income * 0.35),
                "urgency": "medium"
            })
        elif category == "Food" and ratio > 15:
            optimization_suggestions.append({
                "category": category,
                "message": f"Your food expenses are {ratio:.1f}% of your income, which is higher than the typical 10-15%.",
                "potential_savings": amount - (total_income * 0.15),
                "urgency": "medium"
            })
        # Add more rules for other categories
    
    # Create a proper BudgetAnalysis object
    budget_analysis = BudgetAnalysis(
        period_start=period_start,
        period_end=period_end,
        total_income=total_income,
        total_expenses=total_expenses,
        expense_by_category=expense_by_category,
        income_by_source=income_by_source,
        optimization_suggestions=optimization_suggestions,
        # Savings rate and net_cash_flow will be calculated by the model's validator
    )
    
    # Build a text summary of the budget analysis for use in prompts
    budget_analysis_text = f"""
    Income Analysis:
    - Total Monthly Income: {format_currency(total_income)}
    - Income Sources: {len(state.income_sources)}
    
    Expense Analysis:
    - Total Monthly Expenses: {format_currency(total_expenses)}
    - Net Cash Flow: {format_currency(net_cash_flow)}
    - Savings Rate: {budget_analysis.savings_rate:.1f}%
    
    Expense Ratios:
    """ + "\n".join([f"- {category}: {ratio:.1f}%" for category, ratio in expense_ratios.items()])
    
    state.working_memory["budget_analysis_text"] = budget_analysis_text
    
    # Create a suggested budget based on the analysis
    suggested_budget = Budget(
        name=f"Suggested Budget - {today.strftime('%B %Y')}",
        start_date=period_start,
        end_date=period_end,
        income_sources=state.income_sources,
        expenses=state.expenses,
        savings_goal=net_cash_flow if net_cash_flow > 0 else 0
    )
    
    state.working_memory["suggested_budget"] = suggested_budget
    
    return BudgetAgentState(
        user_input=state.user_input,
        income_sources=state.income_sources,
        expenses=state.expenses,
        transactions=state.transactions,
        budget_analysis=budget_analysis,
        current_step="recommend",
        working_memory=state.working_memory,
    )

def generate_recommendations(state: BudgetAgentState) -> BudgetAgentState:
    """Generate budget recommendations based on the analysis."""
    # Format expense breakdown
    if state.budget_analysis:
        expense_breakdown = "\n".join([
            f"- {category}: {format_currency(amount)} ({amount / state.budget_analysis.total_income * 100:.1f}% of income)" 
            for category, amount in state.budget_analysis.expense_by_category.items()
        ])
        
        total_income = state.budget_analysis.total_income
        total_expenses = state.budget_analysis.total_expenses
        net_cash_flow = state.budget_analysis.net_cash_flow
    else:
        expense_breakdown = "No expense data available"
        total_income = 0
        total_expenses = 0
        net_cash_flow = 0
    
    llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL, api_key=settings.ANTHROPIC_API_KEY)
    response = llm.invoke(
        BUDGET_RECOMMENDATION_PROMPT.format(
            total_income=total_income,
            total_expenses=total_expenses,
            net_cash_flow=net_cash_flow,
            expense_breakdown=expense_breakdown,
            budget_analysis=state.working_memory.get("budget_analysis_text", ""),
            user_input=state.user_input,
            financial_goals=state.working_memory.get("financial_goals", "No specific goals mentioned.")
        )
    )
    
    # Prepare data for potential visualizations
    if state.budget_analysis:
        visual_data = {
            "expense_breakdown": {
                "labels": list(state.budget_analysis.expense_by_category.keys()),
                "values": list(state.budget_analysis.expense_by_category.values())
            },
            "monthly_cashflow": {
                "labels": ["Income", "Expenses", "Savings"],
                "values": [
                    state.budget_analysis.total_income,
                    state.budget_analysis.total_expenses,
                    state.budget_analysis.net_cash_flow
                ]
            }
        }
    else:
        visual_data = {}
    
    state.working_memory["visual_data"] = visual_data
    state.working_memory["savings_recommendations"] = state.working_memory.get("savings_allocation", {})
    
    return BudgetAgentState(
        user_input=state.user_input,
        income_sources=state.income_sources,
        expenses=state.expenses,
        transactions=state.transactions,
        budget_analysis=state.budget_analysis,
        current_step="done",
        working_memory=state.working_memory,
        response=response.content
    )

# Define the state graph
def create_budget_agent():
    """Create a budget planning agent workflow."""
    workflow = StateGraph(BudgetAgentState)
    
    # Add nodes
    workflow.add_node("intake", intake_financial_data)
    workflow.add_node("analyze", analyze_budget)
    workflow.add_node("recommend", generate_recommendations)
    
    # Define edges
    workflow.add_edge("intake", "analyze")
    workflow.add_edge("analyze", "recommend")
    workflow.add_edge("recommend", END)
    
    # Set entry point
    workflow.set_entry_point("intake")
    
    # Compile the graph
    return workflow.compile()