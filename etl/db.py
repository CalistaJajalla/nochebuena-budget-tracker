# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st
from psycopg2 import OperationalError

# LOCAL DATABASE
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass",
}

def get_connection():
    """
    Returns a psycopg2 connection.
    - If Streamlit secrets exist → use cloud DB (Supabase)
    - Otherwise → try local Postgres, but safely
    """
    # 1. Cloud DB (Streamlit Secrets)
    if hasattr(st, "secrets") and "database" in st.secrets:
        try:
            conn = psycopg2.connect(
                st.secrets["database"]["url"],
                sslmode="require"
            )
            return conn
        except OperationalError as e:
            st.error(f"Could not connect to cloud DB: {e}")
            st.stop()

    # 2. Local DB
    try:
        conn = psycopg2.connect(**LOCAL_DB)
        return conn
    except OperationalError:
        st.warning(
            "Local database not found. Running without database support.\n"
            "Price trends will not be available."
        )
        return None
