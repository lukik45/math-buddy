from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.solver import solve_problem

router = APIRouter()

class SolveRequest(BaseModel):
    problem: str

class SolveResponse(BaseModel):
    steps: dict

@router.post("/solve", response_model=SolveResponse)
async def solve(req: SolveRequest):
    try:
        result = solve_problem(req.problem)
        return {"steps": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))