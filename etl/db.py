from sqlalchemy import create_engine
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

def get_engine(secrets=None):
    # Cloud: use Supabase Pooler URL if available
    if secrets and "DATABASE_URL" in secrets:
        url = secrets["DATABASE_URL"]
        # Sanitize URL: remove 'pgbouncer=true' if present
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params.pop('pgbouncer', None)
        new_query = urlencode(query_params, doseq=True)
        cleaned_url = urlunparse(parsed._replace(query=new_query))
        return create_engine(cleaned_url, pool_pre_ping=True)

    # Local fallback
    if secrets:
        user = secrets.get("DB_USER")
        password = secrets.get("DB_PASSWORD")
        host = secrets.get("POSTGRES_HOST")
        port = secrets.get("POSTGRES_PORT")
        db = secrets.get("POSTGRES_DB")
    else:
        # default local config
        user = "noche_user"
        password = "noche_pass"
        host = "localhost"
        port = 5432
        db = "nochebuena"

    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url, pool_pre_ping=True)
