# tools/calculator.py
from typing import Dict, List

def calculate_monthly_equivalent(amount: float, frequency: str) -> float:
    """Convert amounts of different frequencies to monthly equivalent."""
    frequency_map = {
        "daily": 30,
        "weekly": 4.33,
        "biweekly": 2.17,
        "monthly": 1,
        "quarterly": 1/3,
        "annually": 1/12,
    }
    
    multiplier = frequency_map.get(frequency.lower(), 1)
    return amount * multiplier

def analyze_expense_ratio(expenses: Dict[str, float], total_income: float) -> Dict[str, float]:
    """Calculate expense to income ratio for each category."""
    ratios = {}
    for category, amount in expenses.items():
        ratios[category] = (amount / total_income) * 100 if total_income > 0 else 0
    return ratios

def suggest_savings_allocation(net_cash_flow: float) -> Dict[str, float]:
    """Suggest how to allocate positive cash flow to savings."""
    if net_cash_flow <= 0:
        return {}
    
    # Simple 50/30/20 allocation for positive cash flow
    return {
        "emergency_fund": net_cash_flow * 0.5,
        "retirement": net_cash_flow * 0.3,
        "personal_goals": net_cash_flow * 0.2
    }