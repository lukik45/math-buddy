from backend.services.llm import SolutionGenerator
from backend.services.matcher import SkillMatcher
from backend.db.neo4j import Neo4jClient
from backend.db.base import SessionLocal
from backend.models.domain.problem import ProblemLog
from backend.core.config import settings
import json
from datetime import datetime

def solve_problem(problem_text: str):
    solutionGenerator = SolutionGenerator()
    initial_solution = solutionGenerator.generate(problem_text)
    matcher = SkillMatcher()
    steps_with_skills = []
    for step in initial_solution.steps:
        matches = matcher.match(step.solution)
        steps_with_skills.append({
            'step_number': step.step_number,
            'hint': step.hint,
            'solution': step.solution,
            'skills': matches
        })
        
    # refine the solution with llm
    print(steps_with_skills)
    refined_solution = solutionGenerator.refine(steps_with_skills)
    
    # db = SessionLocal()
    # log = ProblemLog(
    #     problem=problem_text,
    #     solution=json.dumps(steps_with_skills),
    #     refined_solution=json.dumps(refined_solution),
    #     created_at=datetime.utcnow()
    # )
    # db.add(log)
    # db.commit()
    # db.close()
    # neo4j.close()
    return refined_solution