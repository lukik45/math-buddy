from sqlalchemy import Column, Integer, Text, DateTime
from backend.db.base import Base

class ProblemLog(Base):
    __tablename__ = "problem_logs"
    id = Column(Integer, primary_key=True, index=True)
    problem = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    refined_solution = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)