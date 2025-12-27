# The DB port is for both local/cloud (although you can just use local)

from sqlalchemy import create_engine
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import streamlit as st
import os

def get_engine():
    """
    Return SQLAlchemy engine, using:
    1. Streamlit secrets for Supabase
    2. Local Postgres fallback
    """
    secrets = st.secrets if hasattr(st, "secrets") else {}

    # 1️⃣ Supabase / Cloud
    if "database" in secrets and "url" in secrets["database"]:
        url = secrets["database"]["url"]
        # Clean pgbouncer query if present
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params.pop("pgbouncer", None)
        new_query = urlencode(query_params, doseq=True)
        cleaned_url = urlunparse(parsed._replace(query=new_query))
        return create_engine(cleaned_url, pool_pre_ping=True)

    # 2️⃣ Local fallback
    LOCAL_DB = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", 5432),
        "dbname": os.getenv("POSTGRES_DB", "nochebuena"),
        "user": os.getenv("DB_USER", "noche_user"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
    url = f"postgresql://{LOCAL_DB['user']}:{LOCAL_DB['password']}@{LOCAL_DB['host']}:{LOCAL_DB['port']}/{LOCAL_DB['dbname']}"
    return create_engine(url, pool_pre_ping=True)
