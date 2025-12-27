# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st
import os

# Local fallback
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass"
}

def get_connection():
    """
    Connect to Supabase if DATABASE_URL exists in Streamlit secrets,
    else fallback to local Postgres.
    """
    try:
        if "DATABASE_URL" in st.secrets:
            # Supabase URL from Streamlit secrets
            db_url = st.secrets["DATABASE_URL"]
            conn = psycopg2.connect(db_url, sslmode="require")
        else:
            # Local fallback
            conn = psycopg2.connect(**LOCAL_DB)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.stop()

