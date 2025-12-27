# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st

# Default local config
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass"
}

def get_connection():
    """Return a new database connection"""
    if "database" in st.secrets:
        cfg = st.secrets["database"]
        db_config = {
            "host": cfg["host"],
            "port": cfg["port"],
            "dbname": cfg["name"],
            "user": cfg["user"],
            "password": cfg["pass"]
        }
    else:
        db_config = LOCAL_DB

    return psycopg2.connect(**db_config)
