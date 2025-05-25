import redis
from config import data_config, config
import os




def init_redis_conn():
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



