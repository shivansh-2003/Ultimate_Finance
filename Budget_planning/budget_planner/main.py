# app.py
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'budget_planner.log')
)
logger = logging.getLogger(__name__)

# Import local modules
from agents.budget_agent import create_budget_agent, BudgetAgentState
from models.schema import BudgetRequest, BudgetResponse
from utils.config import Settings
from core.helper import calculate_monthly_equivalent, analyze_expense_ratio, suggest_savings_allocation
# Initialize settings and app
settings = Settings()
app = FastAPI(
    title=os.getenv('APP_NAME', 'Budget Planner'),
    version=os.getenv('APP_VERSION', '1.0.0')
)

# Initialize the budget agent
try:
    budget_agent = create_budget_agent()
except Exception as e:
    logger.error(f"Failed to initialize budget agent: {e}")
    budget_agent = None

@app.post("/api/v1/analyze-budget", response_model=BudgetResponse)
async def analyze_budget(request: BudgetRequest):
    """Analyze budget based on user input."""
    if not budget_agent:
        raise HTTPException(status_code=500, detail="Budget agent not initialized")
    
    try:
        # Initialize the agent state with user input
        initial_state = BudgetAgentState(
            user_input=request.user_input,
            transactions=request.transactions or [],
            working_memory={"timeframe": request.timeframe}
        )
        
        # Run the agent
        result = budget_agent.invoke(initial_state)
        
        # Create a BudgetResponse from the agent result
        response = BudgetResponse(
            budget_analysis=result.budget_analysis,
            recommendations=result.response,
            suggested_budget=result.working_memory.get("suggested_budget"),
            savings_recommendations=result.working_memory.get("savings_recommendations", {}),
            visual_data=result.working_memory.get("visual_data", {})
        )
        
        return response
    except Exception as e:
        logger.error(f"Error processing budget: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing budget: {str(e)}")

def main():
    """Main entry point for the application."""
    import uvicorn
    
    # Get host and port from environment, with defaults
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    logger.info(f"Starting Budget Planner on {host}:{port}")
    
    uvicorn.run(
        "budget_planner.main:app", 
        host=host, 
        port=port, 
        reload=os.getenv('DEBUG', 'false').lower() == 'true'
    )

if __name__ == "__main__":
    main()