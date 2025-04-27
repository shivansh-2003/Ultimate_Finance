# agent/budget_agent.py
from typing import Dict, List, Tuple, Any, Optional
from langchain.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic  # Or ChatOpenAI
from langchain.schema import Document
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# Define the state of our budget agent
class BudgetAgentState(BaseModel):
    user_input: str
    income_data: Optional[List[Dict]] = None
    expense_data: Optional[List[Dict]] = None
    current_step: str = "intake"  # Possible values: intake, analyze, recommend
    working_memory: Dict[str, Any] = Field(default_factory=dict)
    response: Optional[str] = None

# Define the nodes in our graph
def intake_financial_data(state: BudgetAgentState) -> BudgetAgentState:
    """Process initial user input and extract financial information."""
    # Use LLM to extract income and expense information from user input
    prompt = ChatPromptTemplate.from_template(
        """Extract all income and expense information from the user input.
        Format it as structured data.
        
        User input: {user_input}
        
        Return JSON with two keys:
        - income_data: list of income sources with amount and frequency
        - expense_data: list of expenses with category, amount, and frequency
        """
    )
    
    llm = ChatAnthropic(model="claude-3-sonnet-20240229")
    response = llm.invoke(prompt.format(user_input=state.user_input))
    
    # Parse LLM response into structured data
    # This is simplified - you'd need proper JSON parsing
    extracted_data = parse_financial_data(response.content)
    
    return BudgetAgentState(
        user_input=state.user_input,
        income_data=extracted_data.get("income_data", []),
        expense_data=extracted_data.get("expense_data", []),
        current_step="analyze",
        working_memory=state.working_memory,
    )

def analyze_budget(state: BudgetAgentState) -> BudgetAgentState:
    """Analyze income and expenses to create a budget analysis."""
    # Calculate total income and expenses
    total_income = sum(item["amount"] for item in state.income_data or [])
    total_expenses = sum(item["amount"] for item in state.expense_data or [])
    net_cash_flow = total_income - total_expenses
    
    # Group expenses by category
    expense_by_category = {}
    for expense in state.expense_data or []:
        category = expense.get("category", "Other")
        expense_by_category[category] = expense_by_category.get(category, 0) + expense["amount"]
    
    # Store analysis in working memory
    state.working_memory["total_income"] = total_income
    state.working_memory["total_expenses"] = total_expenses
    state.working_memory["net_cash_flow"] = net_cash_flow
    state.working_memory["expense_by_category"] = expense_by_category
    
    return BudgetAgentState(
        user_input=state.user_input,
        income_data=state.income_data,
        expense_data=state.expense_data,
        current_step="recommend",
        working_memory=state.working_memory,
    )

def generate_recommendations(state: BudgetAgentState) -> BudgetAgentState:
    """Generate budget recommendations based on the analysis."""
    prompt = ChatPromptTemplate.from_template(
        """Based on the user's financial situation, provide budget recommendations.
        
        Financial Information:
        - Total Monthly Income: ${total_income}
        - Total Monthly Expenses: ${total_expenses}
        - Net Cash Flow: ${net_cash_flow}
        
        Expense Breakdown:
        {expense_breakdown}
        
        Original User Input: {user_input}
        
        Provide personalized budget recommendations including:
        1. Overall budget assessment
        2. Spending pattern observations
        3. Specific recommendations for improvement
        4. Savings suggestions
        5. Next steps for financial planning
        
        Make your recommendations specific, actionable, and tailored to the user's situation.
        """
    )
    
    # Format expense breakdown
    expense_breakdown = "\n".join([
        f"- {category}: ${amount}" 
        for category, amount in state.working_memory.get("expense_by_category", {}).items()
    ])
    
    llm = ChatAnthropic(model="claude-3-sonnet-20240229")
    response = llm.invoke(
        prompt.format(
            total_income=state.working_memory.get("total_income", 0),
            total_expenses=state.working_memory.get("total_expenses", 0),
            net_cash_flow=state.working_memory.get("net_cash_flow", 0),
            expense_breakdown=expense_breakdown,
            user_input=state.user_input
        )
    )
    
    return BudgetAgentState(
        user_input=state.user_input,
        income_data=state.income_data,
        expense_data=state.expense_data,
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