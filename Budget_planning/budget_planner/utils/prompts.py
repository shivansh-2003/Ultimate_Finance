# agent/prompts.py
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Prompt for extracting financial data from user input
FINANCIAL_DATA_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """You are a financial data extraction assistant. Your task is to carefully analyze user input and extract all 
        relevant income and expense information. Be thorough and precise in your extraction."""
    ),
    HumanMessagePromptTemplate.from_template(
        """Please extract all income and expense information from the following user input:
        
        User Input: {user_input}
        
        Extract and structure the data in the following JSON format:
        
        {{
            "income_data": [
                {{
                    "source": "Source name",
                    "amount": amount as number,
                    "frequency": "frequency (e.g., monthly, weekly, annual)"
                }}
            ],
            "expense_data": [
                {{
                    "description": "Expense description",
                    "amount": amount as number,
                    "category": "expense category",
                    "frequency": "frequency (e.g., monthly, weekly, annual)"
                }}
            ]
        }}
        
        If certain information is not explicitly stated, make reasonable inferences based on context.
        If frequency is not specified, default to monthly.
        Ensure all amounts are represented as numbers without currency symbols.
        """
    )
])

# Prompt for budget analysis
BUDGET_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """You are a budget analysis expert. Your task is to analyze financial data and provide insights
        on spending patterns, income-to-expense ratios, and financial health indicators."""
    ),
    HumanMessagePromptTemplate.from_template(
        """Please analyze the following financial data:
        
        Income Data:
        {income_data}
        
        Expense Data:
        {expense_data}
        
        Basic Calculations:
        - Total Monthly Income: ${total_income}
        - Total Monthly Expenses: ${total_expenses}
        - Net Cash Flow: ${net_cash_flow}
        
        Provide a detailed analysis including:
        1. Income stability assessment
        2. Spending pattern analysis
        3. Major expense categories identification
        4. Income-to-expense ratio analysis
        5. Financial health indicators
        
        Format your analysis in a structured way that can be easily processed for recommendations.
        """
    )
])

# Prompt for budget recommendations
BUDGET_RECOMMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """You are a personal finance advisor specialized in budget planning. Your goal is to provide
        actionable, personalized recommendations that help users improve their financial situation.
        Be specific, practical, and considerate of the user's unique circumstances."""
    ),
    HumanMessagePromptTemplate.from_template(
        """Based on the user's financial situation, provide comprehensive budget recommendations.
        
        Financial Overview:
        - Total Monthly Income: ${total_income}
        - Total Monthly Expenses: ${total_expenses}
        - Net Cash Flow: ${net_cash_flow}
        
        Expense Breakdown:
        {expense_breakdown}
        
        Budget Analysis Insights:
        {budget_analysis}
        
        Original User Context:
        {user_input}
        
        Please provide personalized budget recommendations including:
        
        1. **Overall Budget Assessment**:
           Provide a clear evaluation of the current budget situation.
        
        2. **Spending Optimization**:
           Identify specific categories where spending could be reduced and provide practical suggestions.
        
        3. **Savings Plan**:
           Recommend an appropriate savings strategy based on their cash flow situation.
        
        4. **Debt Management** (if applicable):
           Suggest strategies for managing any mentioned debts efficiently.
        
        5. **Income Enhancement** (if applicable):
           If income is insufficient, suggest potential ways to increase earnings.
        
        6. **Practical Next Steps**:
           Provide 3 concrete, actionable steps the user can take immediately to improve their financial situation.
        
        7. **Long-term Considerations**:
           Brief guidance on longer-term financial planning based on their situation.
        
        Make your recommendations specific, actionable, and tailored to the user's unique situation.
        Use a friendly, supportive tone while remaining professional.
        """
    )
])

# Prompt for expense categorization
EXPENSE_CATEGORIZATION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """You are an expense categorization specialist. Your task is to assign the most appropriate
        financial category to each expense item based on its description."""
    ),
    HumanMessagePromptTemplate.from_template(
        """Please categorize the following expenses into standard financial categories.

        Expenses:
        {expense_list}
        
        For each expense, assign one of the following categories:
        - Housing (rent, mortgage, property taxes, repairs, etc.)
        - Transportation (car payments, gas, public transit, etc.)
        - Food (groceries, dining out, etc.)
        - Utilities (electricity, water, gas, internet, phone, etc.)
        - Healthcare (insurance, medications, doctor visits, etc.)
        - Entertainment (streaming services, hobbies, etc.)
        - Shopping (clothing, electronics, household items, etc.)
        - Education (tuition, books, courses, etc.)
        - Personal Care (haircuts, gym, etc.)
        - Debt Payments (loans, credit cards, etc.)
        - Savings & Investments
        - Insurance (non-health insurance)
        - Gifts & Donations
        - Travel
        - Childcare & Children's Expenses
        - Pets
        - Taxes
        - Miscellaneous

        Return the results in JSON format:
        {{
            "categorized_expenses": [
                {{
                    "description": "original description",
                    "amount": original amount,
                    "category": "assigned category",
                    "frequency": "original frequency"
                }}
            ]
        }}
        """
    )
])

# Prompt for savings recommendations
SAVINGS_RECOMMENDATION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """You are a savings strategy expert. Your task is to recommend optimal savings allocations
        based on a user's financial situation and goals."""
    ),
    HumanMessagePromptTemplate.from_template(
        """Based on the user's financial situation, recommend how they should allocate their savings.
        
        Financial Situation:
        - Total Monthly Income: ${total_income}
        - Total Monthly Expenses: ${total_expenses}
        - Net Cash Flow: ${net_cash_flow}
        
        User Context:
        {user_input}
        
        Current Financial Goals (if mentioned):
        {financial_goals}
        
        Please provide a detailed savings allocation plan including:
        
        1. Recommended Emergency Fund strategy
        2. Short-term savings allocations (0-2 years)
        3. Medium-term savings allocations (2-5 years)
        4. Long-term/retirement savings recommendations
        5. Suggested savings vehicles (accounts, investments, etc.)
        
        Provide specific percentages or amounts for each category where possible.
        If the user has negative cash flow, focus on building emergency savings first
        and suggest ways to increase income or reduce expenses.
        """
    )
])

# Prompt for expense reduction suggestions
EXPENSE_REDUCTION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """You are a frugality and expense optimization expert. Your task is to provide practical, 
        actionable advice for reducing expenses in various budget categories."""
    ),
    HumanMessagePromptTemplate.from_template(
        """Based on the user's expense breakdown, suggest specific ways they could reduce spending
        while maintaining quality of life.
        
        Expense Breakdown:
        {expense_breakdown}
        
        User Context:
        {user_input}
        
        For each major expense category (especially those taking up significant portions of the budget),
        provide 2-3 practical tips for reducing expenses. Focus on:
        
        1. High-impact opportunities first
        2. Quick wins that can be implemented immediately
        3. Long-term structural changes to reduce ongoing expenses
        4. Alternatives that offer similar value at lower cost
        
        Be specific, practical, and respectful of the user's situation.
        Avoid generic advice - tailor suggestions to the specific amounts and categories in their budget.
        """
    )
])