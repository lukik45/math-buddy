from neo4j import GraphDatabase
import numpy as np
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict

from backend.db.neo4j import Neo4jClient
from backend.core.config import settings

from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings


class SkillMatcher:
    def __init__(self, neo4j_client: Neo4jClient=None):
        self.neo4j = neo4j_client
        self.embeddings = OpenAIEmbeddings()
        self.init_vector_store()
        
        
    def init_vector_store(self):
        """
        Connect to the vector store, create the embeddings if they do not exist
        """
        # Initialize the OpenAI Embeddings model
        embedding_model = OpenAIEmbeddings()
        
        #
        self.vector_store = Neo4jVector.from_existing_graph(
            embedding=embedding_model,
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            index_name="skill_vector_index",
            node_label="Skill",
            text_node_properties=["text"],
            embedding_node_property="embedding"
        )

        
    




    def match(self, text: str, k: int = 7) -> List[Dict]:
        """
        Embed the query text and return top-k matched skills.
        """
        matches: List[Dict] = []

        # Perform similarity search
        results = self.vector_store.similarity_search_with_score(text, k=k)

        for doc, score in results:
            skill_id = doc.metadata.get('nodeId')
            skill_text = doc.page_content.strip()
            matches.append({
                'elementId': skill_id,
                'text': skill_text,
                'score': score
            })

        return matches

   
            
        
        


if __name__ == "__main__":
    matcher = SkillMatcher()
    matcher.match("zamienia liczby rzymskie na dziesiętne")
