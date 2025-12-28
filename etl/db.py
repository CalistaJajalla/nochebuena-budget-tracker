# The DB port is for both local/cloud (although you can just use local)

from sqlalchemy import create_engine
import streamlit as st
import os

def get_engine():
    # Supabase (Streamlit Cloud)
    if "database" in st.secrets:
        return create_engine(
            st.secrets["database"]["url"],
            pool_pre_ping=True
        )

    # Local fallback
    return create_engine(
        f"postgresql://{os.getenv('DB_USER','noche_user')}:"
        f"{os.getenv('DB_PASSWORD','')}@"
        f"{os.getenv('POSTGRES_HOST','localhost')}:"
        f"{os.getenv('POSTGRES_PORT','5432')}/"
        f"{os.getenv('POSTGRES_DB','nochebuena')}",
        pool_pre_ping=True
    )
