import redis
from config import data_config

redis_client = None

def init_redis_conn():
    global redis_client
    if redis_client is None:
        host, port = data_config.REDIS_ADDR.split(":")
        redis_client = redis.Redis(
            host=host,
            port=int(port),
            password=data_config.REDIS_PASSWORD,
            db=data_config.REDIS_DB_NO,
            socket_connect_timeout=10,
            socket_timeout=10,
            decode_responses=True
        )
        try:
            redis_client.ping()
        except redis.ConnectionError as e:
            raise Exception(f"Redis连接失败: {e}")
    return redis_client

def close_redis():
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None