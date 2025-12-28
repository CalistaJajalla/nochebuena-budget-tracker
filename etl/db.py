# etl/db.py
from sqlalchemy import create_engine
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import streamlit as st

def get_engine():
    """Return SQLAlchemy engine for Supabase only."""
    
    # Supabase Pooler URL from secrets
    SUPABASE_URL = st.secrets["SUPABASE_URL"]

    # Clean pgbouncer param if present
    parsed = urlparse(SUPABASE_URL)
    query_params = parse_qs(parsed.query)
    query_params.pop("pgbouncer", None)
    new_query = urlencode(query_params, doseq=True)
    cleaned_url = urlunparse(parsed._replace(query=new_query))
    
    # Create engine and test connection
    engine = create_engine(cleaned_url, pool_pre_ping=True)
    with engine.connect() as conn:
        pass  # will raise exception if fails
    
    return engine
