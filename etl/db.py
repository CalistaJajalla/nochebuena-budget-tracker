from sqlalchemy import create_engine
import streamlit as st

# Local DB config
LOCAL_DB = {
    "user": "noche_user",
    "password": "noche_pass",
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
}

def get_engine():
    """
    Connect to Supabase Pooler first, fall back to local Postgres if needed.
    """
    # Try Supabase Pooler from Streamlit secrets
    SUPABASE_URI = st.secrets.get("SUPABASE_URI", "")
    if SUPABASE_URI:
        try:
            engine = create_engine(SUPABASE_URI, pool_pre_ping=True)
            # Test connection
            conn = engine.connect()
            conn.close()
            return engine
        except Exception as e:
            st.warning(f"Supabase connection failed: {e}\nFalling back to local DB.")

    # Fallback to local
    try:
        url = f"postgresql://{LOCAL_DB['user']}:{LOCAL_DB['password']}@{LOCAL_DB['host']}:{LOCAL_DB['port']}/{LOCAL_DB['dbname']}"
        engine = create_engine(url, pool_pre_ping=True)
        # Test connection
        conn = engine.connect()
        conn.close()
        return engine
    except Exception as e:
        st.error(f"No database available: {e}")
        st.stop()
