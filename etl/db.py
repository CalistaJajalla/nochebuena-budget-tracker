# The DB port is for both local/cloud (although you can just use local)

import os
import psycopg2
import streamlit as st
from psycopg2 import OperationalError

# Local DB config (password from env, not in code)
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": os.getenv("LOCAL_DB_PASSWORD")  # optional, set locally
}

def get_connection():
    """
    Connect to Supabase first (via Streamlit secrets), fallback to local.
    """
    # 1️⃣ Try Supabase (Cloud)
    if hasattr(st, "secrets") and "database" in st.secrets:
        supabase_url = st.secrets["database"].get("url")
        if supabase_url:
            try:
                conn = psycopg2.connect(supabase_url, sslmode="require")
                return conn
            except OperationalError as e:
                st.warning("Supabase connection failed, falling back to local DB.")
                print("DEBUG SUPABASE ERROR:", e)

    # 2️⃣ Local fallback
    try:
        conn = psycopg2.connect(**LOCAL_DB)
        return conn
    except OperationalError as e:
        st.error("No DB connection available! Check local DB or Supabase secrets.")
        print("DEBUG LOCAL DB ERROR:", e)
        st.stop()
