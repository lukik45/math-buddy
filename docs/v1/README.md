# Docs for math-buddy's v1 (mvp)

# Problem Statement
Develop a tool, that helps students that has fallen behind.


# User stories

## User story 1: the simplest interaction - Solving the problem
1. User enters the app. 
1. User enters the math problem (via text)
1. System solves the problem, step by step, including hints.
1. User can unfold the next step, see the hint, or click to reveal the solution-step.

## User story 2: Solving the problem with matching with the core curriculum
1. User enters the app.
1. User enters the math problem (via text)
1. System solves the problem, step by step, including hints.
    - to each step, the system finds skills from the core curriculum, that are needed 
    to solve the step. 
1. the user sees the "tree" of math skills, and can see where they had fallen behind.


## User story 3: Solving the problem with matching with the core curriculum, and logging to user's skill tree
1. User enters the app.
1. User enters the math problem (via text)
1. System solves the problem, step by step, including hints.
    - to each step, the system finds skills from the core curriculum, that are needed 
    to solve the step. 
1. the user sees the "tree" of math skills, and can see where they had fallen behind.
1. While solving the problem, user specifies whether they were capable of solving the solution-step 
on their own. The User's skill tree is updated according to the user's feedback


# Technical stack
- Python as a main programming language
- FastAPI as an api connecting all the components
- OpenAI api as LLM and embedding models
- Langchain as a tool for LLM chains
- Neo4j as the knowledge graph
- SQLlite as a relational database (users, user progress)
- no UI in the mvp


# Data
The main data used in the app is the Polish Core curriculum.


