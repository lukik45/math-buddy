import pytest
from backend.services.solver import solve_problem


solution = solve_problem("Monika i Janek mają razem 100 kasztanów. Monika ma o 30 więcej kasztanów niż Janek. Ile kasztanów ma Monika, a ile Janek? Zadanie w czwartej klasie. Uczniowie nie znają wyrażeń algebraicznych")

for step in solution:
    print(step)