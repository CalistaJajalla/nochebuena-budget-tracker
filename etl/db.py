# The DB port is for both local/cloud (although you can just use local)

import os
import psycopg2
import streamlit as st
from psycopg2 import OperationalError


def get_connection():
    """
    Priority:
    1. Supabase via DATABASE_URL (env var)
    2. Local Postgres via PG* env vars
    """

    # 1. Supabase (cloud)
    supabase_url = os.getenv("DATABASE_URL")
    if supabase_url:
        try:
            return psycopg2.connect(
                supabase_url,
                sslmode="require"
            )
        except OperationalError as e:
            st.warning("Supabase connection failed, falling back to local.")

    # 2. Local Postgres (no hardcoded password)
    try:
        return psycopg2.connect(
            host=os.getenv("PGHOST", "localhost"),
            port=os.getenv("PGPORT", "5432"),
            dbname=os.getenv("PGDATABASE", "nochebuena"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
        )
    except OperationalError as e:
        st.error("Database connection failed.")
        st.stop()
