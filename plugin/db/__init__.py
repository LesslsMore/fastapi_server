from sqlmodel import Session

from config.config import load_dotenv
from plugin.db.postgres import init_postgres
from plugin.db.redis_client import init_redis_conn

# config = load_config()
# load_dotenv('../config/.env.win')
load_dotenv('config/.env.win')
# load_dotenv('config/.env.render')
# load_dotenv('config/.env.vercel')
pg_engine = init_postgres()
redis_client = init_redis_conn()


# 获取数据库会话的依赖
def get_session():
    return Session(pg_engine)


def get_redis_client():
    return redis_client


def close_redis():
    redis_client.close()
