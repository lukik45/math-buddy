# full_mvp_test.py

from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import os


### 1. Define Output Schema

class Step(BaseModel):
    step_number: int = Field(..., description="Numer kroku")
    hint: str = Field(..., description="Podpowiedź do kroku")
    solution: str = Field(..., description="Rozwiązanie kroku")
    skills: List[str] = Field(..., description="Lista umiejętności potrzebnych do kroku. przynajmniej 3")

class Solution(BaseModel):
    steps: List[Step] = Field(..., description="Lista kroków rozwiązania")


### 2. Neo4j Connector

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def fetch_all_skills(self):
        query = """
        MATCH (s:Skill)
        RETURN elementID(s) AS id, s.text AS text, s.grade AS grade, s.type AS type
        """
        with self.driver.session() as session:
            results = session.run(query)
            return [dict(record) for record in results]


### 3. LLM Solution Generator (Polish + JSON)

class SolutionGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.2)
        self.parser = JsonOutputParser(pydantic_object=Solution)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Jesteś nauczycielem matematyki. Generujesz rozwiązania krok po kroku."),
            ("human", "Zadanie: {problem}\n\n{format_instructions}")
        ]).partial(format_instructions=self.parser.get_format_instructions())
        self.chain = self.prompt | self.llm | self.parser
        
    def generate(self, problem: str) -> Solution:
        result = self.chain.invoke({"problem": problem})
        return Solution(**result)



### 4. Matcher with FAISS

class SkillMatcher:
    def __init__(self, skills: List[dict]):
        self.embeddings = OpenAIEmbeddings()
        self.skills = skills
        self.docstore = self._build_vectorstore()

    def _build_vectorstore(self):
        documents = [
            Document(page_content=skill["text"], metadata={"elementID": skill["id"], **skill})
            for skill in self.skills
        ]
        return FAISS.from_documents(documents, self.embeddings)

    def match(self, text: str, k: int = 3):
        matches = self.docstore.similarity_search(text, k=k)
        return [{"elementID": m.metadata["elementID"], "text": m.page_content} for m in matches]


### 5. Main Orchestration

def main():
    # Connect to Neo4j
    kg = Neo4jClient("bolt://localhost:7687", "neo4j", "password")
    skills = kg.fetch_all_skills()
    print(f"📘 Załadowano {len(skills)} umiejętności z grafu.")

    # Problem input
    problem = """
    Mama Natalii zamierza kupić nową pralkę. Pierwsza wpłata wynosi 460 zł. 
    Pozostała kwota ma być spłacona w 12 miesięcznych ratach po 95 zł.
    Ile kosztuje ta pralka?
    """

    # Generate structured solution
    solver = SolutionGenerator()
    print("\n🧠 Generowanie rozwiązania przez GPT...")
    solution = solver.generate(problem)
    print(solution)

    # Match skills
    matcher = SkillMatcher(skills)
    print("\n🔍 Dopasowywanie umiejętności:")

    for step in solution.steps:
        print(f"\nKrok {step.step_number}: {step.solution}")
        matched = matcher.match(step.solution)
        for skill in matched:
            print(f" - {skill['elementID']}: {skill['text']}")

    kg.close()


if __name__ == "__main__":
    os.environ["LANGCHAIN_TRACING_V2"] = "false"  # optional
    main()
