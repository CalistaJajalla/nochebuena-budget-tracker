# etl/db.py
from sqlalchemy import create_engine
import streamlit as st

def get_engine():
    """
    Attempt connection to Supabase Direct URI first.
    Fallback to local Postgres if needed.
    """
    # Supabase Direct connection from Streamlit secrets
    SUPABASE_URI = st.secrets.get("SUPABASE_URI")  # e.g., postgresql://postgres:<password>@db.admnjjcsgnvpqemgmmip.supabase.co:5432/postgres

    if SUPABASE_URI:
        try:
            engine = create_engine(SUPABASE_URI, pool_pre_ping=True)
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except Exception as e:
            st.warning(f"Supabase connection failed: {e}")

    # Local fallback (optional, only if Postgres is running locally)
    LOCAL_DB = {
        "user": "noche_user",
        "password": "noche_pass",
        "host": "localhost",
        "port": 5432,
        "dbname": "nochebuena",
    }
    try:
        url = f"postgresql://{LOCAL_DB['user']}:{LOCAL_DB['password']}@{LOCAL_DB['host']}:{LOCAL_DB['port']}/{LOCAL_DB['dbname']}"
        engine = create_engine(url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"No DB available: {e}")
        st.stop()
