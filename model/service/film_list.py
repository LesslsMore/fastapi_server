import json
from redis import Redis
from typing import List

from config.privide_config import FILM_CLASS_KEY
from model.system.film_list import FilmClass
from plugin.db.redis_client import get_redis_client, init_redis_conn

# Assuming Redis is already configured and connected
# redis_client = Redis()

# FILM_CLASS_KEY = 'film_class_key'
RESOURCE_EXPIRED = 3600  # Example expiration time in seconds


def save_film_class(list: List[FilmClass]) -> None:
    redis_client = get_redis_client() or init_redis_conn()
    data = json.dumps([film for film in list])
    redis_client.set(FILM_CLASS_KEY, data, ex=RESOURCE_EXPIRED)


def get_film_class() -> List[FilmClass]:
    redis_client = get_redis_client() or init_redis_conn()
    data = redis_client.get(FILM_CLASS_KEY)
    if data:
        return [FilmClass(**film) for film in json.loads(data)]
    return []