# utils/helpers.py
import json
import re
from typing import Dict, List, Any, Tuple, Optional, Union
from datetime import datetime, date, timedelta
import logging
from .config import settings

# Setup logging
logger = logging.getLogger(__name__)

def parse_financial_data(text: str) -> Dict[str, Any]:
    """
    Extract structured financial data from LLM-generated text.
    
    Args:
        text: The text containing financial data, potentially in JSON format
        
    Returns:
        Dictionary with extracted financial data
    """
    # Try to find JSON in the text
    json_pattern = r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}'
    json_match = re.search(json_pattern, text)
    
    if json_match:
        json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
        # Clean up the string to ensure it's valid JSON
        json_str = json_str.strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
    
    # If no JSON found or parsing failed, return an empty structure
    logger.info("No valid JSON found in text, returning empty structure")
    return {"income_data": [], "expense_data": []}

def format_currency(amount: float, currency: str = None) -> str:
    """
    Format a number as currency.
    
    Args:
        amount: The amount to format
        currency: The currency code (default from settings)
        
    Returns:
        Formatted currency string
    """
    currency = currency or settings.DEFAULT_CURRENCY
    
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    elif currency == "INR":
        return f"₹{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_budget_adherence(planned: float, actual: float) -> Tuple[float, str]:
    """
    Calculate budget adherence percentage and status.
    
    Args:
        planned: Planned amount
        actual: Actual amount
        
    Returns:
        Tuple of (adherence_percentage, status)
        Status can be 'under', 'on_track', or 'over'
    """
    if planned <= 0:
        return 0.0, "unknown"
    
    adherence = (actual / planned) * 100
    
    if adherence < 95:
        status = "under"
    elif adherence <= 105:
        status = "on_track"
    else:
        status = "over"
        
    return adherence, status

def generate_date_range(start_date: Union[str, date], 
                       end_date: Union[str, date]) -> List[date]:
    """
    Generate a list of dates between start and end dates.
    
    Args:
        start_date: Start date (string or date object)
        end_date: End date (string or date object)
        
    Returns:
        List of date objects
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
        
    return date_list

def normalize_transaction_data(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize transaction data to ensure consistent format.
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Normalized transaction list
    """
    normalized = []
    
    for transaction in transactions:
        norm_transaction = transaction.copy()
        
        # Ensure date is in correct format
        if isinstance(norm_transaction.get('date'), str):
            try:
                norm_transaction['date'] = datetime.strptime(
                    norm_transaction['date'], "%Y-%m-%d"
                ).date()
            except ValueError:
                logger.warning(f"Invalid date format in transaction: {norm_transaction.get('date')}")
                continue
        
        # Ensure amount is a float
        if 'amount' in norm_transaction:
            try:
                norm_transaction['amount'] = float(norm_transaction['amount'])
            except (ValueError, TypeError):
                logger.warning(f"Invalid amount in transaction: {norm_transaction.get('amount')}")
                continue
        
        # Ensure description exists
        if 'description' not in norm_transaction or not norm_transaction['description']:
            norm_transaction['description'] = "Unknown transaction"
        
        normalized.append(norm_transaction)
    
    return normalized

def extract_financial_info_from_text(text: str) -> Dict[str, Any]:
    """
    Extract financial information from unstructured text using regex patterns.
    This is a fallback method when LLM extraction fails.
    
    Args:
        text: Text containing financial information
        
    Returns:
        Dictionary with extracted financial data
    """
    result = {
        "income_data": [],
        "expense_data": []
    }
    
    # Extract income
    income_patterns = [
        r'(?:income|salary|earn|make|paid|pay|getting|get)\s+(?:of\s+)?[$€£₹]?\s?(\d+[,\d]*(?:\.\d+)?)\s+(?:per\s+)?(annually|yearly|monthly|weekly|biweekly|daily)',
        r'[$€£₹]?\s?(\d+[,\d]*(?:\.\d+)?)\s+(?:in\s+)?(?:income|salary)'
    ]
    
    for pattern in income_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                frequency = match.group(2) if len(match.groups()) > 1 else "monthly"
                
                result["income_data"].append({
                    "source": "Income",
                    "amount": amount,
                    "frequency": frequency or "monthly"
                })
            except (ValueError, IndexError):
                continue
    
    # Extract expenses
    expense_patterns = [
        r'(?:spend|spent|pay|paid|cost|costs|expense|expenses)\s+(?:of\s+)?[$€£₹]?\s?(\d+[,\d]*(?:\.\d+)?)\s+(?:on|for)\s+([a-zA-Z\s]+)(?:\s+(?:per\s+)?(annually|yearly|monthly|weekly|biweekly|daily))?',
        r'([a-zA-Z\s]+)\s+(?:cost|costs|is|are)\s+[$€£₹]?\s?(\d+[,\d]*(?:\.\d+)?)(?:\s+(?:per\s+)?(annually|yearly|monthly|weekly|biweekly|daily))?'
    ]
    
    for pattern in expense_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            groups = match.groups()
            if len(groups) >= 2:
                # The pattern order varies between the two regex patterns
                if groups[0].replace(',', '').replace('.', '').isdigit():
                    amount_str = groups[0].replace(',', '')
                    category = groups[1].strip()
                    frequency = groups[2] if len(groups) > 2 else "monthly"
                else:
                    amount_str = groups[1].replace(',', '')
                    category = groups[0].strip()
                    frequency = groups[2] if len(groups) > 2 else "monthly"
                
                try:
                    amount = float(amount_str)
                    result["expense_data"].append({
                        "description": category,
                        "amount": amount,
                        "category": category,
                        "frequency": frequency or "monthly"
                    })
                except ValueError:
                    continue
    
    return result