from fastapi import FastAPI
from backend.core.config import settings
from backend.db.base import engine, Base
from backend.services.matcher import SkillMatcher
from backend.db.neo4j import Neo4jClient
from backend.api.v1.solve import router as solve_router



# Create SQL tables
Base.metadata.create_all(bind=engine)

# Define lifespan function to replace deprecated on_event decorators
async def lifespan(app: FastAPI):
    # Startup
    neo4j = Neo4jClient(settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    matcher = SkillMatcher(neo4j)

    app.state.neo4j = neo4j
    app.state.matcher = matcher
    yield
    # Shutdown
    app.state.neo4j.close()

# Instantiate FastAPI with lifespan handler
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Include API router
app.include_router(solve_router, prefix="/api/v1")
