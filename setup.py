# setup.py
from setuptools import setup, find_packages

setup(
    name="math_buddy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "neo4j",
        "sqlalchemy",
        "pydantic",
        "python-dotenv",
        "openai",
        "langchain",
        "langchain-openai",
        "pytest"
    ],
    include_package_data=True,
)
