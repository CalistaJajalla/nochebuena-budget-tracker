# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st

# LOCAL DATABASE (for people running locally)
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass",
}

def get_connection():
    """
    - If Streamlit secrets exist → Supabase
    - Otherwise → Local Postgres
    """

    # Streamlit Cloud OR local user who added secrets
    if hasattr(st, "secrets") and "database" in st.secrets:
        return psycopg2.connect(
            st.secrets["database"]["url"],
            sslmode="require"
        )

    # Pure local fallback
    return psycopg2.connect(**LOCAL_DB)
