# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st
from psycopg2 import OperationalError

LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass",
}

def get_connection():
    """Try Supabase first, then local."""
    # Cloud DB
    if "database" in st.secrets:
        try:
            return psycopg2.connect(st.secrets["database"]["url"], sslmode="require")
        except OperationalError as e:
            st.warning(f"Supabase connection failed: {e}\nFalling back to local DB.")

    # Local DB fallback
    try:
        return psycopg2.connect(**LOCAL_DB)
    except OperationalError as e:
        st.error(f"No DB available: {e}")
        st.stop()
