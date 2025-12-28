# The DB port is for both local/cloud (although you can just use local)

# etl/db.py
from sqlalchemy import create_engine
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import streamlit as st

def get_engine():
    """
    Returns a SQLAlchemy engine using Supabase Pooler if available,
    otherwise local DB for development.
    """
    secrets = st.secrets

    # Cloud: Supabase Pooler URL
    if "SUPABASE_URL" in secrets:
        url = secrets["SUPABASE_URL"]
        # Remove pgbouncer query param if present
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params.pop("pgbouncer", None)
        new_query = urlencode(query_params, doseq=True)
        cleaned_url = urlunparse(parsed._replace(query=new_query))
        return create_engine(cleaned_url, pool_pre_ping=True)

    # Local: fallback DB (only for dev/testing)
    user = secrets.get("DB_USER", "noche_user")
    password = secrets.get("DB_PASSWORD", "noche_pass")
    host = secrets.get("POSTGRES_HOST", "localhost")
    port = secrets.get("POSTGRES_PORT", "5432")
    db = secrets.get("POSTGRES_DB", "nochebuena")
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url, pool_pre_ping=True)
