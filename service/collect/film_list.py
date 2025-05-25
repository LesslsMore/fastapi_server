import json
from typing import List

from config.privide_config import FILM_CLASS_KEY, RESOURCE_EXPIRED
from model.collect.film_list import FilmClass
from plugin.db import get_redis_client, init_redis_conn




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