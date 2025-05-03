#!/bin/bash
# Script to load data into Neo4j when running in Docker

# The environment variables are already set by docker-compose
echo "Using Neo4j connection: $NEO4J_URI"

# Wait for Neo4j initialization
echo "Waiting for Neo4j to fully initialize..."
sleep 10

# Run data loaders
echo "Loading core curriculum data..."
cd /app
python -m data_processing.loaders.load_core_curriculum

echo "Loading skills data..."
python -m data_processing.loaders.load_skills

echo "✅ Data loading complete!"