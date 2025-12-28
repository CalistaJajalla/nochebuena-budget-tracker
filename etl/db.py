# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st
from psycopg2 import OperationalError

def get_connection():
    """
    Priority:
    1. Supabase via Session Pooler
    2. Local Postgres fallback
    """

    # 1. Supabase session pooler
    if "database" in st.secrets:
        url = st.secrets["database"]["url"]  # Should be pooler URL
        try:
            conn = psycopg2.connect(url, sslmode="require")
            st.info("Connected to Supabase session pooler")
            return conn
        except OperationalError as e:
            st.warning(f"Supabase session pooler connection failed: {e}. Falling back to local DB.")

    # 2. Local Postgres fallback (no hardcoded password)
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            dbname="nochebuena",
            user="noche_user",
            password="",  # Empty password for local
        )
        st.info("Connected to local Postgres")
        return conn
    except OperationalError as e:
        st.error(f"Local database connection failed: {e}")
        st.stop()
