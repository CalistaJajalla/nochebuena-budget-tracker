# The DB port is for both local/cloud (although you can just use local)

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

def get_connection():
    """
    Connect to Supabase via direct URI first (IPv6 compatible).
    Fallback to local Postgres if Supabase fails.
    """
    supabase_uri = st.secrets.get("SUPABASE_URL", "")
    if supabase_uri:
        try:
            return psycopg2.connect(supabase_uri, sslmode="require")
        except OperationalError as e:
            st.warning(f"Supabase connection failed: {e}\nFalling back to local DB.")

    try:
        return psycopg2.connect(**LOCAL_DB)
    except OperationalError as e:
        st.error(f"No DB available: {e}")
        st.stop()
