# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st
from psycopg2 import OperationalError
import os

# Determine environment
RUNNING_LOCALLY = os.getenv("RUNNING_LOCALLY", "0") == "1"

# Local Postgres config (for testing on local machine)
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass",
}

def get_connection():
    """
    Connect to Supabase (Cloud) or local DB (only if running locally).
    """
    # Supabase URI from secrets
    SUPABASE_URI = st.secrets.get("SUPABASE_URL", "")
    if SUPABASE_URI:
        try:
            return psycopg2.connect(SUPABASE_URI, sslmode="require")
        except OperationalError as e:
            st.error(f"Supabase connection failed: {e}")
            st.stop()

    # Only attempt local if explicitly running locally
    if RUNNING_LOCALLY:
        try:
            return psycopg2.connect(**LOCAL_DB)
        except OperationalError as e:
            st.error(f"Local DB connection failed: {e}")
            st.stop()

    # If here, no DB is available
    st.error("No database available. Supabase URI not set or connection failed.")
    st.stop()
