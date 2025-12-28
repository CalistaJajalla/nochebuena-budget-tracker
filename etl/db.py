# The DB port is for both local/cloud (although you can just use local)

import os
import psycopg2
import streamlit as st
from psycopg2 import OperationalError

# LOCAL DATABASE CONFIG
LOCAL_DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
    "dbname": os.getenv("PGDATABASE", "nochebuena"),
    "user": os.getenv("PGUSER", "noche_user"),
    "password": os.getenv("PGPASSWORD", "noche_pass"),
}

def get_connection():
    """Try Supabase first, fallback to local."""
    
    # Supabase session pooler
    if "database" in st.secrets and "url" in st.secrets["database"]:
        url = st.secrets["database"]["url"]
        try:
            return psycopg2.connect(url)
        except OperationalError as e:
            st.warning(f"Supabase connection failed: {e}\nFalling back to local DB.")

    # Local fallback
    try:
        return psycopg2.connect(**LOCAL_DB_CONFIG)
    except OperationalError as e:
        st.error(f"Local DB connection failed: {e}")
        st.stop()
