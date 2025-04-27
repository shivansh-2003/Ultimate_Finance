# app.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from budget_agent import create_budget_agent, BudgetAgentState

app = FastAPI(title="Budget Planning Assistant")

# Initialize the budget agent
budget_agent = create_budget_agent()

class BudgetRequest(BaseModel):
    user_input: str

class BudgetResponse(BaseModel):
    response: str

@app.post("/analyze-budget", response_model=BudgetResponse)
async def analyze_budget(request: BudgetRequest):
    """Analyze budget based on user input."""
    try:
        # Initialize the agent state with user input
        initial_state = BudgetAgentState(user_input=request.user_input)
        
        # Run the agent
        result = budget_agent.invoke(initial_state)
        
        return BudgetResponse(response=result.response or "Unable to generate recommendations.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing budget: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)