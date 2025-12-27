# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st

# Local fallback DB config
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass"
}

def get_connection():
    """
    Connects to Supabase (Streamlit secrets) if available, else local Postgres.
    Returns a psycopg2 connection object.
    """
    try:
        # Try Streamlit secrets first (Supabase)
        cfg = st.secrets.get("database")
        if cfg:
            db_config = {
                "host": cfg["host"],
                "port": cfg["port"],
                "dbname": cfg["name"],
                "user": cfg["user"],
                "password": cfg["pass"],
                "sslmode": "require"
            }
        else:
            # Fallback to local
            db_config = LOCAL_DB

        # Attempt connection
        conn = psycopg2.connect(**db_config)
        return conn

    except Exception as e:
        # Show a friendly error in Streamlit
        st.error("Database connection failed. See logs for details.")
        st.stop()

        db_config = LOCAL_DB
        print("Connecting to local Postgres...")

    return psycopg2.connect(**db_config)

