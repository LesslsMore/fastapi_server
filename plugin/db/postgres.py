from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import Engine
from typing import Optional
from config import data_config, config
from sqlmodel import Session
import os


def init_postgres():
    postgres_url = os.environ.get("POSTGRES_URL")
    if postgres_url:
        db_url = postgres_url
    else:
        pg = config['postgres']
        db_url = f"postgresql+psycopg2://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['db']}"
    pg_engine = create_engine(db_url, echo=True, pool_pre_ping=True)
    return pg_engine



