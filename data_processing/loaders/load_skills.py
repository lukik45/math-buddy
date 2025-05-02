import pandas as pd
import ast
from neo4j import GraphDatabase
from pathlib import Path

# === Neo4j Configuration ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"  # Change this!

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / ".." / "data" / "04_processed_data"

# === Grades you want to process ===
GRADES_TO_PROCESS = ['4', '5', '6', '7', '8']
# GRADES_TO_PROCESS = ['4']

def determine_level(grade):
    """
    Given an individual grade (string), determine the curriculum level.
    For example, grades 4,5,6 map to level "4-6" and grades 7,8 map to level "7-8".
    """
    if grade in ['4', '5', '6']:
        return "4-6"
    elif grade in ['7', '8']:
        return "7-8"
    else:
        return grade  # fallback in case of other grades

class SkillConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def connect_skills(self, grade, df):
        # Determine the curriculum level based on grade.
        level = determine_level(grade)
        
        # Ensure we have valid chapter_requirements data
        df = df.dropna(subset=["chapter_requirements"])
        with self.driver.session() as session:
            for _, row in df.iterrows():
                # Parse chapter_requirements; expected format: [(chapter_num, req_num), ...]
                chapter_reqs = row.get("chapter_requirements")
                if isinstance(chapter_reqs, str):
                    try:
                        chapter_reqs = ast.literal_eval(chapter_reqs)
                    except Exception:
                        chapter_reqs = []
                # Parse skill lists (for basic and advanced skills)
                basic_skills = row.get("Cele podstawowe", [])
                advanced_skills = row.get("Cele ponadpodstawowe", [])
                if isinstance(basic_skills, str):
                    try:
                        basic_skills = ast.literal_eval(basic_skills)
                    except Exception:
                        basic_skills = []
                if isinstance(advanced_skills, str):
                    try:
                        advanced_skills = ast.literal_eval(advanced_skills)
                    except Exception:
                        advanced_skills = []
                        
                # For each requirement indicated in the row, link all skills.
                for chapter_num, req_num in chapter_reqs:
                    # Add basic skills
                    for skill_text in basic_skills:
                        session.execute_write(
                            self._link_skill_to_requirement,
                            chapter_num, req_num, skill_text, "basic", grade, level
                        )
                    # Add advanced skills
                    for skill_text in advanced_skills:
                        session.execute_write(
                            self._link_skill_to_requirement,
                            chapter_num, req_num, skill_text, "advanced", grade, level
                        )

    @staticmethod
    def _link_skill_to_requirement(tx, chapter_num, req_num, skill_text, skill_type, grade, level):
        if not skill_text:
            return
        # Use the determined level (e.g., "4-6" or "7-8") in matching.
        tx.run("""
            MERGE (s:Skill {text: $skill_text})
            ON CREATE SET s.uuid = randomUUID()
            SET s.type = $skill_type, s.level = $level, s.nodeId = elementId(s)
            WITH s
            MATCH (c:Chapter {number: $chap_num, level: $level})-[:HAS_REQUIREMENT]->(r:Requirement {number: $req_num})
            MERGE (r)-[:INVOLVES_SKILL]->(s)
        """, skill_text=skill_text,
             skill_type=skill_type,
             level=level,
             grade=grade,
             chap_num=chapter_num,
             req_num=req_num)

def main():
    connector = SkillConnector(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

    for grade in GRADES_TO_PROCESS:
        print(f"\n▶️ Processing grade {grade}...")
        csv_path = PROCESSED_DIR / f"merged_grade_{grade}.csv"
        if not csv_path.exists():
            print(f"⚠️ File not found: {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        connector.connect_skills(grade, df)

    connector.close()
    print("\n✅ All skills connected to requirements in Neo4j.")

if __name__ == "__main__":
    main()
