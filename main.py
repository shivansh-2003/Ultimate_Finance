# main.py
from fastapi import FastAPI
from planning import agent as planning_agent
from budget import agent as budget_agent

app = FastAPI()

@app.post("/generate-financial-plan/")
async def generate_financial_plan(user_input: str):
    response = planning_agent.print_response(user_input, stream=True)
    return {"response": response}

@app.post("/analyze-budget/")
async def analyze_budget(user_input: str):
    response = budget_agent.print_response(user_input, stream=True)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)