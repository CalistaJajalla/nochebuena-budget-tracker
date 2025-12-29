from sqlalchemy import create_engine

# LOCAL CONFIG
LOCAL_DB = {
    "user": "noche_user",
    "password": "noche_pass",
    "host": "localhost",
    "port": 5432,
    "db": "nochebuena",
}


def get_engine(secrets=None, use_local=False):
    """
    Supabase-first.
    Local DB is used ONLY if use_local=True.
    """

    # Local
    if use_local:
        url = (
            f"postgresql://{LOCAL_DB['user']}:{LOCAL_DB['password']}"
            f"@{LOCAL_DB['host']}:{LOCAL_DB['port']}/{LOCAL_DB['db']}"
        )
        return create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5},
        )

    # Supabase
    if not secrets or "DATABASE_URL" not in secrets:
        raise RuntimeError(
            "Supabase DATABASE_URL missing. "
            "Do not fall back to localhost in cloud."
        )

    return create_engine(
        secrets["DATABASE_URL"].strip(),
        pool_pre_ping=True,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 5,
        },
    )
