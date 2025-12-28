# The DB port is for both local/cloud (although you can just use local)

# etl/db.py
import psycopg2
import streamlit as st
from psycopg2 import OperationalError
import os
import socket

# Local Postgres config (for dev only)
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass",
}

def get_connection():
    """
    Attempt connection to Supabase session pooler first (for cloud/Streamlit deployment).
    If running locally, fallback to local Postgres.
    """
    # Check if running on Streamlit Cloud or local machine
    running_locally = os.environ.get("STREAMLIT_SERVER_PORT") is None

    if not running_locally:
        # Supabase Pooler config from secrets
        supabase = st.secrets["SUPABASE"]
        try:
            conn = psycopg2.connect(
                host=supabase["SUPABASE_HOST"],
                port=int(supabase["SUPABASE_PORT"]),
                dbname=supabase["SUPABASE_DB"],
                user=supabase["SUPABASE_USER"],
                password=supabase["SUPABASE_PASSWORD"],
                sslmode="require",
            )
            return conn
        except OperationalError as e:
            st.error(f"Supabase connection failed: {e}")
            st.stop()

    # Local fallback (for dev machine)
    try:
        return psycopg2.connect(**LOCAL_DB)
    except OperationalError as e:
        st.error(f"Local DB connection failed: {e}")
        st.stop()
