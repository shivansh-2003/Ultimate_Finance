# tools/categorizer.py
from typing import Dict, List, Tuple, Optional, Union, Any
import re
import json
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum, auto

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoryType(Enum):
    """Enum representing different types of expense categories."""
    ESSENTIAL = auto()      # Necessary expenses (housing, utilities, etc.)
    DISCRETIONARY = auto()  # Optional expenses (entertainment, dining out)
    SAVINGS = auto()        # Savings and investments
    DEBT = auto()           # Debt payments
    INCOME = auto()         # Income sources
    OTHER = auto()          # Uncategorized

@dataclass
class Category:
    """Represents a financial category with metadata."""
    name: str
    keywords: List[str]
    type: CategoryType
    description: str
    subcategories: Optional[List['Category']] = None
    parent: Optional['Category'] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary for serialization."""
        result = {
            "name": self.name,
            "keywords": self.keywords,
            "type": self.type.name,
            "description": self.description
        }
        if self.subcategories:
            result["subcategories"] = [sub.to_dict() for sub in self.subcategories]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional['Category'] = None) -> 'Category':
        """Create a Category from a dictionary."""
        subcategories = None
        if "subcategories" in data:
            subcategories = []
        
        category = cls(
            name=data["name"],
            keywords=data["keywords"],
            type=CategoryType[data["type"]],
            description=data["description"],
            subcategories=subcategories,
            parent=parent
        )
        
        if "subcategories" in data:
            category.subcategories = [
                cls.from_dict(subcat, parent=category) 
                for subcat in data["subcategories"]
            ]
            
        return category


class ExpenseCategorizer:
    """A robust system for categorizing financial transactions."""
    
    def __init__(self, categories_file: Optional[str] = None):
        """Initialize the categorizer with categories from file or defaults."""
        self.categories: List[Category] = []
        self.category_map: Dict[str, Category] = {}
        
        if categories_file and Path(categories_file).exists():
            self._load_categories_from_file(categories_file)
        else:
            self._load_default_categories()
            
        # Build a lookup map for efficient access
        self._build_category_map()
    
    def _load_categories_from_file(self, file_path: str) -> None:
        """Load categories from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                categories_data = json.load(f)
            
            self.categories = [
                Category.from_dict(cat_data) for cat_data in categories_data
            ]
            logger.info(f"Loaded {len(self.categories)} categories from {file_path}")
        except Exception as e:
            logger.error(f"Error loading categories from {file_path}: {e}")
            # Fall back to defaults
            self._load_default_categories()
    
    def _load_default_categories(self) -> None:
        """Load a default set of categories."""
        self.categories = [
            Category(
                name="Housing", 
                keywords=["rent", "mortgage", "property tax", "maintenance", "repairs", 
                         "housing", "apartment", "house", "lease", "landlord", "tenant"],
                type=CategoryType.ESSENTIAL,
                description="Housing and shelter expenses",
                subcategories=[
                    Category(
                        name="Rent",
                        keywords=["rent", "lease", "apartment"],
                        type=CategoryType.ESSENTIAL,
                        description="Rental payments",
                        parent=None  # Will be set after creation
                    ),
                    Category(
                        name="Mortgage",
                        keywords=["mortgage", "home loan", "housing loan"],
                        type=CategoryType.ESSENTIAL,
                        description="Mortgage payments",
                        parent=None
                    ),
                    Category(
                        name="Home Maintenance",
                        keywords=["maintenance", "repairs", "renovation", "improvement"],
                        type=CategoryType.ESSENTIAL,
                        description="Home maintenance and repairs",
                        parent=None
                    )
                ]
            ),
            Category(
                name="Transportation", 
                keywords=["car", "gas", "fuel", "uber", "lyft", "taxi", "public transport", 
                         "bus", "train", "subway", "commute", "fare", "toll", "parking"],
                type=CategoryType.ESSENTIAL,
                description="Transportation expenses",
                subcategories=[
                    Category(
                        name="Public Transit",
                        keywords=["bus", "train", "subway", "metro", "public transport", "fare"],
                        type=CategoryType.ESSENTIAL,
                        description="Public transportation expenses",
                        parent=None
                    ),
                    Category(
                        name="Car Expenses",
                        keywords=["car", "gas", "fuel", "maintenance", "repair", "oil", "tire"],
                        type=CategoryType.ESSENTIAL,
                        description="Car-related expenses",
                        parent=None
                    ),
                    Category(
                        name="Ride Services",
                        keywords=["uber", "lyft", "taxi", "cab", "ride share", "rideshare"],
                        type=CategoryType.DISCRETIONARY,
                        description="Ride-sharing and taxi services",
                        parent=None
                    )
                ]
            ),
            # Add more categories similar to the above pattern
            Category(
                name="Food", 
                keywords=["grocery", "restaurant", "dining", "food", "meal", "takeout", 
                         "delivery", "supermarket", "snack", "breakfast", "lunch", "dinner"],
                type=CategoryType.ESSENTIAL,
                description="Food and dining expenses",
                subcategories=[
                    Category(
                        name="Groceries",
                        keywords=["grocery", "supermarket", "food store", "produce", "groceries"],
                        type=CategoryType.ESSENTIAL,
                        description="Grocery purchases",
                        parent=None
                    ),
                    Category(
                        name="Restaurants",
                        keywords=["restaurant", "dining", "takeout", "delivery", "cafe", "diner"],
                        type=CategoryType.DISCRETIONARY,
                        description="Restaurant and dining out expenses",
                        parent=None
                    )
                ]
            ),
            # Continue with other categories...
            # For brevity, I'm including fewer categories than would be ideal for a production system
        ]
        
        # Set parent references for subcategories
        for category in self.categories:
            if category.subcategories:
                for subcategory in category.subcategories:
                    subcategory.parent = category
    
    def _build_category_map(self) -> None:
        """Build a flat map of all categories and subcategories for quick lookup."""
        self.category_map = {}
        
        def add_to_map(category: Category) -> None:
            self.category_map[category.name.lower()] = category
            if category.subcategories:
                for subcategory in category.subcategories:
                    add_to_map(subcategory)
        
        for category in self.categories:
            add_to_map(category)
    
    def save_categories(self, file_path: str) -> bool:
        """Save categories to a JSON file."""
        try:
            categories_data = [cat.to_dict() for cat in self.categories]
            with open(file_path, 'w') as f:
                json.dump(categories_data, f, indent=2)
            logger.info(f"Saved {len(self.categories)} categories to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving categories to {file_path}: {e}")
            return False
    
    def categorize_transaction(self, description: str, amount: float = 0, 
                              additional_info: Optional[Dict[str, Any]] = None) -> Tuple[Category, float]:
        """
        Categorize a transaction based on description and other available information.
        
        Args:
            description: Transaction description
            amount: Transaction amount (positive for income, negative for expense)
            additional_info: Any additional transaction data that might help with categorization
            
        Returns:
            A tuple of (category, confidence_score)
        """
        if not description:
            return self.get_category_by_name("Other"), 0.0
        
        description = description.lower()
        best_match = None
        best_score = 0
        
        # Check for exact matches in category names
        for name, category in self.category_map.items():
            if name in description:
                return category, 1.0
        
        # Look for keyword matches
        for category in self.categories:
            score = self._calculate_match_score(description, category)
            
            # Check subcategories too
            if category.subcategories:
                for subcategory in category.subcategories:
                    subscore = self._calculate_match_score(description, subcategory)
                    if subscore > score:
                        score = subscore
                        best_match = subcategory
                        best_score = score
                        continue
            
            if score > best_score:
                best_score = score
                best_match = category
        
        # If no good match found
        if best_score < 0.1 or best_match is None:
            return self.get_category_by_name("Other"), 0.0
            
        return best_match, best_score
    
    def _calculate_match_score(self, description: str, category: Category) -> float:
        """Calculate how well a description matches a category based on keywords."""
        score = 0.0
        for keyword in category.keywords:
            if keyword in description:
                # Add to score based on keyword specificity (length)
                score += 0.1 + (len(keyword) / 100)
        return min(score, 1.0)  # Cap at 1.0
    
    def get_category_by_name(self, name: str) -> Category:
        """Get a category by its name."""
        name_lower = name.lower()
        if name_lower in self.category_map:
            return self.category_map[name_lower]
        
        # If not found, return or create an "Other" category
        if "other" in self.category_map:
            return self.category_map["other"]
        else:
            other_category = Category(
                name="Other",
                keywords=[],
                type=CategoryType.OTHER,
                description="Uncategorized transactions"
            )
            self.categories.append(other_category)
            self.category_map["other"] = other_category
            return other_category
    
    def get_all_categories(self) -> List[Category]:
        """Get all top-level categories."""
        return self.categories
    
    def get_all_category_names(self, include_subcategories: bool = False) -> List[str]:
        """Get all category names."""
        if include_subcategories:
            return list(self.category_map.keys())
        else:
            return [category.name for category in self.categories]
    
    def add_category(self, category: Category) -> None:
        """Add a new category to the system."""
        self.categories.append(category)
        self._build_category_map()  # Rebuild the map
    
    def add_keyword_to_category(self, category_name: str, keyword: str) -> bool:
        """Add a keyword to an existing category."""
        if category_name.lower() in self.category_map:
            category = self.category_map[category_name.lower()]
            if keyword.lower() not in [k.lower() for k in category.keywords]:
                category.keywords.append(keyword.lower())
                return True
        return False


class BudgetAnalyzer:
    """Analyzes categorized expenses and provides optimization suggestions."""
    
    def __init__(self, categorizer: ExpenseCategorizer):
        self.categorizer = categorizer
    
    def analyze_spending_by_category(self, transactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Group transactions by category and sum amounts."""
        spending_by_category = {}
        
        for transaction in transactions:
            description = transaction.get('description', '')
            amount = transaction.get('amount', 0)
            
            # Skip non-expense transactions
            if amount >= 0:
                continue
                
            # Get absolute value for expenses
            amount = abs(amount)
            
            # Categorize the transaction
            category, _ = self.categorizer.categorize_transaction(
                description, amount, transaction
            )
            
            # Add to the appropriate category sum
            category_name = category.name
            if category_name in spending_by_category:
                spending_by_category[category_name] += amount
            else:
                spending_by_category[category_name] = amount
                
        return spending_by_category
    
    def analyze_spending_over_time(self, transactions: List[Dict[str, Any]], 
                                  time_key: str = 'date') -> Dict[str, Dict[str, float]]:
        """Analyze spending trends over time by category."""
        time_series = {}
        
        for transaction in transactions:
            if time_key not in transaction or 'description' not in transaction:
                continue
                
            time_period = transaction[time_key]
            description = transaction['description']
            amount = transaction.get('amount', 0)
            
            # Skip non-expense transactions
            if amount >= 0:
                continue
                
            # Get absolute value for expenses
            amount = abs(amount)
            
            # Categorize the transaction
            category, _ = self.categorizer.categorize_transaction(
                description, amount, transaction
            )
            
            # Add to the time series
            if time_period not in time_series:
                time_series[time_period] = {}
                
            category_name = category.name
            if category_name in time_series[time_period]:
                time_series[time_period][category_name] += amount
            else:
                time_series[time_period][category_name] = amount
                
        return time_series
    
    def suggest_expense_optimization(self, spending_by_category: Dict[str, float], 
                                   income: float) -> List[Dict[str, Any]]:
        """
        Suggest categories where spending could be optimized.
        More sophisticated than the original implementation.
        """
        suggestions = []
        total_expenses = sum(spending_by_category.values())
        
        # Calculate what percentage of expenses each category represents
        category_percentages = {
            category: (amount / total_expenses) * 100 
            for category, amount in spending_by_category.items()
        }
        
        # Ideal percentages by category (simplified example)
        ideal_percentages = {
            "Housing": 30,
            "Transportation": 15,
            "Food": 15,
            "Utilities": 10,
            "Healthcare": 10,
            "Entertainment": 5,
            "Shopping": 5,
            "Education": 5,
            "Personal": 5,
            "Debt": 0,  # Handled separately
            "Other": 5
        }
        
        # Check for categories exceeding ideal percentages
        for category, percentage in category_percentages.items():
            ideal = ideal_percentages.get(category, 5)  # Default to 5% if not specified