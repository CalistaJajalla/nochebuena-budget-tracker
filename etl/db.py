# The DB port is for both local/cloud (although you can just use local)

import os
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "nochebuena"),
    "user": os.environ.get("DB_USER", "noche_user"),
    "password": os.environ.get("DB_PASS", "noche_pass"),
}

def get_connection():
    """Return a new database connection"""
    return psycopg2.connect(**DB_CONFIG)
