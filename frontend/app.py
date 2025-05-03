import streamlit as st
import requests
import json

st.title("Problem Solver")

# Input text area for user to enter a word problem
problem = st.text_area("Enter your problem:", 
    "Monika i Janek mają razem 100 kasztanów. Monika ma o 30 więcej kasztanów niż Janek. Ile kasztanów ma Monika, a ile Janek? Zadanie w czwartej klasie. Uczniowie nie znają wyrażeń algebraicznych")

if st.button("Solve Problem"):
    # url = "http://127.0.0.1:8000/api/v1/solve"
    url = "http://backend:8000/api/v1/solve"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "problem": problem
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        st.subheader("API Response")
        st.json(result)
    except requests.exceptions.RequestException as e:
        st.error(f"Error contacting API: {e}")
