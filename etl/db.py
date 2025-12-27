# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st

# Use Supabase info directly (SSL required)
DB_CONFIG = {
    "host": "db.admnjjcsgnvpqemgmmip.supabase.co",  # Supabase host
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "El4dSzda4TZHxj2i",
    "sslmode": "require"   # important for cloud
}

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.stop()

