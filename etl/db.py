# The DB port is for both local/cloud (although you can just use local)

import psycopg2
import streamlit as st
import os

import psycopg2
import streamlit as st
import os

# Local fallback (used only on your machine)
LOCAL_DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass"
}

def get_connection():
    """
    - Streamlit Cloud → Supabase (via secrets)
    - Local machine → localhost Postgres
    """

    # ---- STREAMLIT CLOUD ----
    if "STREAMLIT_RUNTIME" in os.environ:
        try:
            return psycopg2.connect(
                st.secrets["database"]["url"],
                sslmode="require"
            )
        except Exception as e:
            st.error("Supabase connection failed")
            st.exception(e)
            st.stop()

    # ---- LOCAL DEV ----
    return psycopg2.connect(**LOCAL_DB)
