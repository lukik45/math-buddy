from neo4j import GraphDatabase
from pathlib import Path
import json

# === Neo4j Configuration ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"  # Change this!
NEO4J_DATABASE = "neo4j"  # You can change this if using multiple databases

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent
FILES = [
    BASE_DIR / ".." / "data" / "04_processed_data" / "realizacja_podstawy_4_6.json",
    BASE_DIR / ".." / "data" / "04_processed_data" / "realizacja_podstawy_7_8.json"
]

# === Neo4j Importer ===
class CoreCurriculumImporter:
    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("🧹 Database cleared.")

    def insert_curriculum(self, data):
        with self.driver.session(database=self.database) as session:
            for i, chapter in enumerate(data, start=1):
                session.execute_write(self._create_chapter_with_requirements, chapter, i)

    @staticmethod
    def _create_chapter_with_requirements(tx, chapter, chapter_index):
        # Format nodeId for Chapter, starting from 1
        chapter_id = f"chapter-{chapter_index:06d}"

        # Merge Chapter node with nodeId
        tx.run("""
            MERGE (c:Chapter {level: $level, number: $chap_number})
            SET c.name = $chap_name,
                c.nodeId = $chapter_id
        """, level=chapter["level"], chap_number=chapter["number"],
            chap_name=chapter["name"], chapter_id=chapter_id)

        # Merge Requirements and link
        for req_index, req in enumerate(chapter.get("requirements", []), start=1):
            # Format: req-<chapterIndex:03d>-<reqIndex:06d>
            req_id = f"req-{chapter_index:03d}-{req_index:06d}"

            tx.run("""
                MERGE (r:Requirement {number: $req_number, name: $req_name})
                SET r.nodeId = $req_id
                WITH r
                MATCH (c:Chapter {level: $level, number: $chap_number})
                MERGE (c)-[:HAS_REQUIREMENT]->(r)
            """, req_number=req["number"], req_name=req["name"],
                req_id=req_id, level=chapter["level"], chap_number=chapter["number"])

# === Run the full import ===
def main():
    importer = CoreCurriculumImporter(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, database=NEO4J_DATABASE)

    importer.clear_database()  # Start fresh each time (optional but recommended)

    for file in FILES:
        print(f"📂 Importing from: {file.name}")
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        importer.insert_curriculum(data)

    importer.close()
    print("✅ Curriculum successfully imported into Neo4j.")

if __name__ == "__main__":
    main()
