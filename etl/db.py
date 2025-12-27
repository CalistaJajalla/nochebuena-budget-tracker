# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st
import os

# Local database (used ONLY when running locally)
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass"
}

def get_connection():
    """
    - Streamlit Cloud  → Supabase
    - Local machine    → Local Postgres
    """

    # ---- STREAMLIT CLOUD ----
    if os.getenv("STREAMLIT_RUNTIME"):
        return psycopg2.connect(
            st.secrets["database"]["url"],
            sslmode="require"
        )

    # ---- LOCAL ----
    return psycopg2.connect(**LOCAL_DB)
