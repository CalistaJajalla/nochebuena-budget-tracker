# The DB port is for both local/cloud (although you can just use local)

# etl/db.py
import psycopg2
import streamlit as st
from psycopg2 import OperationalError
import os

# Local Postgres config
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass",
}

def get_connection():
    """
    Attempt connection to Supabase session pooler first.
    If it fails, fall back to local Postgres.
    """
    # Supabase config from secrets (do NOT hardcode your password)
    SUPABASE_POOLER = {
        "host": st.secrets.get("SUPABASE_HOST", ""),
        "port": int(st.secrets.get("SUPABASE_PORT", 5432)),
        "dbname": st.secrets.get("SUPABASE_DB", ""),
        "user": st.secrets.get("SUPABASE_USER", ""),
        "password": st.secrets.get("SUPABASE_PASSWORD", ""),
        "sslmode": "require",
    }

    # Try Supabase session pooler
    try:
        if all(SUPABASE_POOLER.values()):
            conn = psycopg2.connect(**SUPABASE_POOLER)
            return conn
    except OperationalError as e:
        st.warning(f"Supabase connection failed: {e}\nFalling back to local DB.")

    # Fall back to local DB
    try:
        return psycopg2.connect(**LOCAL_DB)
    except OperationalError as e:
        st.error(f"No DB available: {e}")
        st.stop()
