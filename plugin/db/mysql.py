from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import Engine
from fastapi import FastAPI
from fastapi import Request
from fastapi import Depends
from typing import Optional
from config import data_config
from sqlmodel import Session

# 全局数据库引擎变量
db_engine: Optional[Engine] = None

def init_mysql():
    global db_engine
    if db_engine is None:
        db_url = f"mysql+pymysql://{data_config.MYSQL_USER}:{data_config.MYSQL_PASSWORD}@{data_config.MYSQL_HOST}:{data_config.MYSQL_PORT}/{data_config.MYSQL_DB}?charset=utf8mb4"
        db_engine = create_engine(db_url, echo=True, pool_pre_ping=True)

# 获取数据库引擎的依赖
def get_db_engine():
    if db_engine is None:
        raise RuntimeError("Database engine is not initialized. Call init_mysql() first.")
    return db_engine

# 获取数据库会话的依赖
def get_db():
    db_url = f"mysql+pymysql://{data_config.MYSQL_USER}:{data_config.MYSQL_PASSWORD}@{data_config.MYSQL_HOST}:{data_config.MYSQL_PORT}/{data_config.MYSQL_DB}?charset=utf8mb4"
    db_engine = create_engine(db_url, echo=True, pool_pre_ping=True)
    return Session(db_engine)
