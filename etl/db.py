# The DB port is for both local/cloud (although you can just use local)

from sqlalchemy import create_engine
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import streamlit as st
import os


def get_engine():
    """
    Priority:
    1. Streamlit Cloud / Supabase via secrets["DATABASE_URL"]
    2. Local Postgres via hardcoded defaults or env vars
    """

    # ---------- CLOUD / SUPABASE ----------
    if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
        url = st.secrets["DATABASE_URL"]

        # Clean Supabase pooler params if present
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        query.pop("pgbouncer", None)

        cleaned_url = urlunparse(
            parsed._replace(query=urlencode(query, doseq=True))
        )

        return create_engine(
            cleaned_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=2
        )

    # ---------- LOCAL FALLBACK ----------
    LOCAL_DB = {
        "user": os.getenv("DB_USER", "noche_user"),
        "password": os.getenv("DB_PASSWORD", "noche_pass"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "db": os.getenv("DB_NAME", "nochebuena"),
    }

    local_url = (
        f"postgresql://{LOCAL_DB['user']}:{LOCAL_DB['password']}"
        f"@{LOCAL_DB['host']}:{LOCAL_DB['port']}/{LOCAL_DB['db']}"
    )

    return create_engine(local_url, pool_pre_ping=True)
