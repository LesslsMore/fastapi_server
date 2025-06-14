from urllib.parse import urlparse

from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import Engine
from typing import Optional
from config import data_config, config
from sqlmodel import Session
import os


def init_postgres():
    postgres_url = os.environ.get("POSTGRES_URL")
    if postgres_url:
        result = urlparse(postgres_url)
        user = result.username  # postgres.kudppysekvoztpnmsvyt
        password = result.password  # 4Dr2x8zEK1hiOktb
        host = result.hostname  # aws-0-ap-southeast-1.pooler.supabase.com
        port = result.port or 5432  # 6543
        database = result.path[1:] if result.path else None  # postgres
        db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    else:
        pg = config['postgres']
        db_url = f"postgresql+psycopg2://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['db']}"
    pg_engine = create_engine(db_url, echo=True, pool_pre_ping=True)
    return pg_engine



