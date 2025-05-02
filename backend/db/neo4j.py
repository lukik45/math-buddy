from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def fetch_all_skills(self):
        query = """
        MATCH (s:Skill)
        RETURN elementId(s) AS id, s.text AS text
        """
        with self.driver.session() as session:
            results = session.run(query)
            return [dict(record) for record in results]

    def set_skill_embedding(self, skill_id: str, vector: list):
        query = """
        MATCH (s:Skill)
        WHERE elementId(s) = $id
        SET s.embedding = $vector
        """
        with self.driver.session() as session:
            session.run(query, id=skill_id, vector=vector)

    def create_gds_vector_index(self, index_name: str = "SkillIndex"):
        drop = f"CALL gds.vector.index.drop('{index_name}')"
        create = f"""
        CALL gds.vector.index.create(
          '{index_name}',
          {{nodeLabels:['Skill'], vectorProperties:['embedding']}}
        )
        """
        with self.driver.session() as session:
            try: session.run(drop)
            except: pass
            session.run(create)

    def knn_query(self, input_vector: list, k: int = 3, index_name: str = "SkillIndex"):
        query = f"""
        CALL gds.vector.knn.stream(
          '{index_name}',
          {{vector:$vector, topK:$k}}
        ) YIELD nodeId, score
        RETURN elementId(gds.util.asNode(nodeId)) AS id, score
        ORDER BY score DESC
        """
        with self.driver.session() as session:
            res = session.run(query, vector=input_vector, k=k)
            return [dict(r) for r in res]
