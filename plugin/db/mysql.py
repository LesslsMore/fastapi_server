from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import Engine
from config import data_config, config
from sqlmodel import Session
import os

def init_mysql():
    mysql_url = os.environ.get("MYSQL_URL")
    if mysql_url:
        db_url = mysql_url
    else:
        mysql = config['mysql']
        db_url = f"mysql+pymysql://{mysql['user']}:{mysql['password']}@{mysql['host']}:{mysql['port']}/{mysql['db']}?charset=utf8mb4"
    db_engine = create_engine(db_url, echo=True, pool_pre_ping=True)
    return db_engine


# 获取数据库会话的依赖
def get_db():
    mysql = config['mysql']
    db_url = f"mysql+pymysql://{mysql['user']}:{mysql['password']}@{mysql['host']}:{mysql['port']}/{mysql['db']}?charset=utf8mb4"
    db_engine = create_engine(db_url, echo=True, pool_pre_ping=True)
    return Session(db_engine)
