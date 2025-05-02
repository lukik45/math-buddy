from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.models.schemas.solution import Solution, SolutionRefined
from backend.core.config import settings
from typing import List, Dict

class SolutionGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", api_key=settings.OPENAI_API_KEY)


    def generate(self, problem: str) -> Solution:
        parser = JsonOutputParser(pydantic_object=Solution)
        prompt = ChatPromptTemplate.from_messages([
            ("system","jesteś dokładnym i szczegółowym korepetytorem matematyki. Wygeneruj rozwiązanie problemu krok po kroku."),
            ("human","Problem: {problem}\n\n{format_instructions}. Proszę podaj odpowiedź w postaci JSON")
        ]).partial(format_instructions=parser.get_format_instructions())
        chain = prompt | self.llm | parser
        result = chain.invoke({"problem": problem})
        return Solution(**result)
    
    def refine(self, solution_steps: List) -> Solution:
        
        parser = JsonOutputParser(pydantic_object=SolutionRefined)
        prompt = ChatPromptTemplate.from_messages([
            ("system","jesteś dokładnym i szczegółowym korepetytorem matematyki. ponizej podano rozwiązanie wraz z potencjalnie powiazanymi umiejetnosciami znalezionymi w bazie danych. Dla kazdego kroku(step) wybierz te umiejetnosci(skills), ktore naprawde sa potrzebne do rozwiazania kroku."),
            ("human","Problem: {problem}\n\n{format_instructions}. Proszę podaj odpowiedź w postaci JSON")
        ]).partial(format_instructions=parser.get_format_instructions())
        chain = prompt | self.llm | parser
        
        result = chain.invoke({"problem": solution_steps})
        return Solution(**result)
