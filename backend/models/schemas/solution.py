from pydantic import BaseModel, Field
from typing import List, Dict

class Step(BaseModel):
    step_number: int = Field(..., description="Step number")
    hint: str = Field(..., description="Podpowiedź dotycząca kroku")
    solution: str = Field(..., description="Pełne rozwiązanie")
    skills: List = Field(..., description="Dopasowane umiejętności (skills)")


class Skill(BaseModel):
    elementId: str = Field(...)
    text: str = Field(...)
    score: float = Field(...)
    
class StepRefined(Step):
    skills: List[Skill] = Field(..., description="Dopasowane umiejętności (skills)")

 
class Solution(BaseModel):
    steps: List[Step]


class SolutionRefined(BaseModel):
    steps: List[StepRefined]