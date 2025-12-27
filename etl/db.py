# The DB port is for both local/cloud (although you can just use local)

import os
import psycopg2
import streamlit as st
from psycopg2 import OperationalError

def get_connection():
    """
    Connect to Supabase (primary) or fallback to local Postgres if needed.
    """
    # 1️⃣ Supabase connection from env
    supabase_url = os.getenv("SUPABASE_URL")
    if supabase_url:
        try:
            conn = psycopg2.connect(supabase_url, sslmode="require")
            return conn
        except OperationalError as e:
            st.warning(f"Supabase connection failed: {e}")

    # 2️⃣ Optional local fallback
    LOCAL_DB = {
        "host": "localhost",
        "port": 5432,
        "dbname": "nochebuena",
        "user": "noche_user",
        "password": os.getenv("LOCAL_DB_PASSWORD")  # optional
    }
    try:
        return psycopg2.connect(**LOCAL_DB)
    except OperationalError as e:
        st.error(f"No DB available: {e}")
        st.stop()
