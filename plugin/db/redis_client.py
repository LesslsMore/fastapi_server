import redis
from config import data_config, config
import os

redis_client: redis.Redis = None

def init_redis_conn():
    global redis_client
    if redis_client is None:
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            redis_client = redis.from_url(redis_url, decode_responses=True)
            try:
                redis_client.ping()
            except redis.ConnectionError as e:
                raise Exception(f"Redis连接失败: {e}")
        else:
            cfg = config['redis']
            host = cfg['host']
            port = cfg['port']
            redis_client = redis.Redis(
                host=host,
                port=int(port),
                password=cfg['password'],
                db=cfg['db_no'],
                socket_connect_timeout=10,
                socket_timeout=10,
                decode_responses=True
            )
            try:
                redis_client.ping()
            except redis.ConnectionError as e:
                raise Exception(f"Redis连接失败: {e}")
    return redis_client

def get_redis_client():
    return redis_client

def close_redis():
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None