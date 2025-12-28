# The DB port is for both local/cloud (although you can just use local)

# etl/db.py
import os
import psycopg2
import streamlit as st
from psycopg2 import OperationalError

# Local Postgres configuration
LOCAL_DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
    "dbname": os.getenv("PGDATABASE", "nochebuena"),
    "user": os.getenv("PGUSER", "noche_user"),
    "password": os.getenv("PGPASSWORD", "noche_pass"),
}

# Supabase session pooler configuration (set these in Streamlit secrets or environment variables)
SUPABASE_POOLER_CONFIG = {
    "host": os.getenv("SUPABASE_HOST", "aws-1-ap-south-1.pooler.supabase.com"),
    "port": int(os.getenv("SUPABASE_PORT", 5432)),
    "dbname": os.getenv("SUPABASE_DB", "postgres"),
    "user": os.getenv("SUPABASE_USER", "postgres"),
    "password": os.getenv("SUPABASE_PASSWORD", ""),
    "sslmode": "require"
}


def get_connection():
    """Try Supabase session pooler first, fallback to local Postgres."""
    
    # 1. Try Supabase
    try:
        conn = psycopg2.connect(**SUPABASE_POOLER_CONFIG)
        return conn
    except OperationalError as e:
        st.warning(f"Supabase pooler connection failed: {e}. Falling back to local Postgres.")

    # 2. Fallback to local
    try:
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        return conn
    except OperationalError as e:
        st.error(f"Local Postgres connection failed: {e}")
        st.stop()
