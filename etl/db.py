# The DB port is for both local/cloud (although you can just use local)

import os
import psycopg2
import streamlit as st

# Check if running in Streamlit Cloud or local
if "SECRETS" in st.secrets:  # Streamlit Cloud
    DB_CONFIG = {
        "host": st.secrets["database"]["host"],
        "port": st.secrets["database"]["port"],
        "dbname": st.secrets["database"]["name"],
        "user": st.secrets["database"]["user"],
        "password": st.secrets["database"]["pass"]
    }
else:  # Local fallback
    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "dbname": "nochebuena",
        "user": "noche_user",
        "password": "noche_pass"
    }

def get_connection():
    """Return a new database connection"""
    return psycopg2.connect(**DB_CONFIG)
