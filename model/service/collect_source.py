from typing import List, Optional
import json
from model.system.collect_source import FilmSource, SourceGrade
from plugin.db.redis_client import redis_client, init_redis_conn
from config.data_config import FILM_SOURCE_LIST_KEY


def get_collect_source(sl: List[str]) -> List[FilmSource]:
    """
    将字符串列表转换为FilmSource对象列表
    :param sl: 字符串列表
    :return: FilmSource对象列表
    """
    l = []
    for s in sl:
        f = FilmSource(**json.loads(s))
        l.append(f)
    return l


def get_collect_source_list_by_grade(grade: SourceGrade) -> List[FilmSource]:
    """
    返回指定类型的采集Api信息 Master | Slave
    :param grade: 采集站等级
    :return: FilmSource对象列表
    """

    # 将grade转换为字符串作为score范围
    score = str(grade.value)
    # 查询指定score范围的采集站点信息
    redis = redis_client or init_redis_conn()
    zl = redis.zrangebyscore(FILM_SOURCE_LIST_KEY, min=score, max=score)
    return get_collect_source(zl)