# Math Buddy - Problem Solver

A tool that helps students who have fallen behind by solving math problems step-by-step and connecting each step to relevant skills from the educational curriculum.

## Features

- Solve math problems with detailed step-by-step explanations
- Match each solution step to relevant skills from the core curriculum
- Track student progress and identify knowledge gaps

## Running with Docker

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

### Setup

1. Clone this repository
   ```bash
   git clone <repository-url>
   cd math-buddy
   ```

2. Create a `.env` file from the template
   ```bash
   cp .env.template .env
   ```

3. Edit the `.env` file and add your OpenAI API key
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Build and start the Docker containers
   ```bash
   docker-compose up -d
   ```

5. Load the curriculum data into Neo4j
   ```bash
   docker exec -it math-buddy-backend ./load_data.sh
   ```

6. Access the application
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474 (username: neo4j, password: password)

### Usage

1. Open the Streamlit frontend at http://localhost:8501
2. Enter a math problem in the text area
3. Click "Solve Problem" to see the step-by-step solution
4. Each solution step will be linked to relevant curriculum skills

## Project Structure

- `backend/`: FastAPI backend service
  - `api/`: API endpoints
  - `core/`: Core configurations
  - `db/`: Database connections
  - `models/`: Data models
  - `services/`: Business logic
- `frontend/`: Streamlit frontend
- `data_processing/`: Data processing scripts
  - `loaders/`: Scripts to load data into Neo4j
  - `scripts/`: Data preprocessing scripts
- `tests/`: Test cases

## Development

For local development without Docker, you'll need:
- Python 3.9+
- Neo4j 5.x
- OpenAI API key

1. Install dependencies
   ```bash
   pip install -e .
   ```

2. Set up environment variables
   ```bash
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Run the backend server
   ```bash
   uvicorn backend.main:app --reload
   ```

4. Run the frontend
   ```bash
   streamlit run frontend/app.py
   ```

## Testing

Run the tests with:
```bash
pytest
```