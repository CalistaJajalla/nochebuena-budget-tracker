# The DB port is for both local/cloud (although you can just use local)

import os
import psycopg2
from dotenv import load_dotenv

# Load .env if present (local dev)
load_dotenv()

# DATABASE CONFIG
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),      # fallback to localhost
    "port": int(os.getenv("DB_PORT", 5432)),       # fallback to 5432
    "dbname": os.getenv("DB_NAME", "nochebuena"),  # fallback to local db name
    "user": os.getenv("DB_USER", "noche_user"),    # fallback to local user
    "password": os.getenv("DB_PASSWORD", "noche_pass")  # fallback to local password
}

def get_connection():
    """Return a new database connection"""
    return psycopg2.connect(**DB_CONFIG)
