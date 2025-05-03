#!/bin/bash
# Script to load data into Neo4j when running in Docker

# Determine if we're running in Docker or not
if [ -f "/.dockerenv" ]; then
  # We're in Docker, use the Docker service name
  CONNECT_HOST="neo4j"
  echo "Running in Docker. Connecting to Neo4j at $CONNECT_HOST."
else
  # We're on the host machine, use localhost
  CONNECT_HOST="localhost"
  echo "Running on host. Connecting to Neo4j at $CONNECT_HOST."
fi

# Export variables for Python scripts
export NEO4J_URI="bolt://$CONNECT_HOST:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"

# Function to check if Neo4j is ready
check_neo4j() {
  echo "Checking Neo4j connection..."
  if [ -f "/.dockerenv" ]; then
    # In Docker, use netcat to check
    nc -z $CONNECT_HOST 7687 && return 0 || return 1
  else
    # On host, use curl or other available tool
    curl -s http://$CONNECT_HOST:7474 >/dev/null && return 0 || return 1
  fi
}

# Wait for Neo4j to start
echo "Waiting for Neo4j to start..."
MAX_RETRIES=30
RETRY_COUNT=0

while ! check_neo4j; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Failed to connect to Neo4j after $MAX_RETRIES attempts. Exiting."
    exit 1
  fi
  echo "Neo4j not ready yet (attempt $RETRY_COUNT/$MAX_RETRIES). Waiting 5 seconds..."
  sleep 5
done

echo "Neo4j is up and running! Starting data loaders..."

# Additional wait to ensure Neo4j is fully initialized
sleep 10

# Show Neo4j connection details
echo "Using Neo4j connection: $NEO4J_URI"

# Run data loaders with error handling
echo "Loading core curriculum data..."
python -m data_processing.loaders.load_core_curriculum
if [ $? -ne 0 ]; then
  echo "Error loading core curriculum data. Please check logs."
  exit 1
fi

echo "Loading skills data..."
python -m data_processing.loaders.load_skills
if [ $? -ne 0 ]; then
  echo "Error loading skills data. Please check logs."
  exit 1
fi

echo "✅ Data loading complete!"