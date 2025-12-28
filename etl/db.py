# The DB port is for both local/cloud (although you can just use local)

# etl/db.py
import psycopg2
import streamlit as st
from psycopg2 import OperationalError

# Local Postgres config
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass",
}

# Supabase session pooler config (replace these with your actual pooler credentials)
SUPABASE_POOLER = {
    "host": "aws-1-ap-south-1.pooler.supabase.com",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "El4dSzda4TZHxj2i",
    "sslmode": "require",
}

def get_connection():
    """
    Attempt connection to Supabase session pooler first.
    If it fails, fall back to local Postgres.
    """
    try:
        conn = psycopg2.connect(**SUPABASE_POOLER)
        return conn
    except OperationalError as e:
        st.warning(f"Supabase connection failed: {e}\nFalling back to local DB.")

    try:
        return psycopg2.connect(**LOCAL_DB)
    except OperationalError as e:
        st.error(f"No DB available: {e}")
        st.stop()
