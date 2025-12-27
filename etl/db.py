# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st

# Local fallback config
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass"
}

def get_connection():
    try:
        # Supabase / Streamlit Cloud
        cfg = st.secrets["database"]
        db_config = {
            "host": cfg["host"],
            "port": cfg["port"],
            "dbname": cfg["name"],
            "user": cfg["user"],
            "password": cfg["pass"],
            "sslmode": "require"  # Supabase requires SSL
        }
        print("Connecting to Supabase...")
    except Exception:
        # Local fallback
        db_config = LOCAL_DB
        print("Connecting to local Postgres...")

    return psycopg2.connect(**db_config)

