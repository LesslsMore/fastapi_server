from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import Engine
from fastapi import FastAPI
from fastapi import Request
from fastapi import Depends
from typing import Optional
from config import data_config, config
from sqlmodel import Session

# 全局数据库引擎变量
pg_engine: Optional[Engine] = None

import os


def init_postgres():
    global pg_engine
    if pg_engine is None:
        postgres_url = os.environ.get("POSTGRES_URL")
        if postgres_url:
            db_url = postgres_url
        else:
            pg = config['postgres']
            db_url = f"postgresql+psycopg2://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['db']}"
        pg_engine = create_engine(db_url, echo=True, pool_pre_ping=True)


# 获取数据库引擎的依赖
def get_db_engine():
    if pg_engine is None:
        raise RuntimeError("Database engine is not initialized. Call init_postgres() first.")
    return pg_engine


# 获取数据库会话的依赖
def get_db():
    return Session(pg_engine)
