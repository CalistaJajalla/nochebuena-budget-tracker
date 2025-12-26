import psycopg2

# DATABASE CONFIG
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "nochebuena",
    "user": "noche_user",
    "password": "noche_pass"
}

def get_connection():
    """Return a new database connection"""
    return psycopg2.connect(**DB_CONFIG)
