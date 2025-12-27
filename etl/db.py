# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st
from psycopg2 import OperationalError

LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass",
}

def get_connection():
    """
    Priority:
    1. Supabase (Streamlit secrets)
    2. Local Postgres (only if running)
    """

    # 1️⃣ SUPABASE (Cloud)
    if "database" in st.secrets:
        try:
            return psycopg2.connect(
                st.secrets["database"]["url"],
                sslmode="require"
            )
        except OperationalError as e:
            st.error("❌ Supabase connection failed.")
            st.exception(e)
            st.stop()  # HARD STOP — do NOT fallback silently

    # 2️⃣ LOCAL POSTGRES (DEV ONLY)
    try:
        return psycopg2.connect(**LOCAL_DB)
    except OperationalError:
        st.error(
            "❌ No database available.\n\n"
            "• Supabase not configured\n"
            "• Local PostgreSQL not running\n\n"
            "Line graphs require a database."
        )
        st.stop()
