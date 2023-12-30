import logging, os
from sqlalchemy import create_engine, URL
from pkg.models import Base

def genv(r, t=str, v=True):
    if not isinstance(os.environ.get(r), t):
        e = f"Please set {r} env var"
        if v:
            logging.error(e)
            print(e, flush=True)
        raise ValueError(e)
    else:
        return os.environ.get(r)

def create_engine_from_env():

    db_user = genv("DB_USERNAME")
    db_host = genv("DB_HOST")
    db_name = genv("DB_NAME")
    db_pass = genv("DB_PASS")

    url = URL.create(
        drivername="postgresql",
        username=db_user,
        host=db_host,
        database=db_name,
    )

    engine = create_engine(url)

    Base.metadata.create_all(engine)

    conn = engine.connect()
    if conn.closed:
        raise ValueError("PostgreSQL not connected")

    return engine

