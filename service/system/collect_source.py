from typing import List, Optional
import json
from model.system.collect_source import FilmSource, SourceGrade
from plugin.common.util.string_util import generate_salt
from plugin.db import redis_client
from config.data_config import FILM_SOURCE_LIST_KEY



def get_collect_source(sl: List[str]) -> List[FilmSource]:
    """
    将字符串列表转换为FilmSource对象列表
    :param sl: 字符串列表
    :return: FilmSource对象列表
    """
    film_source_list = []
    for s in sl:
        film_source = FilmSource(**json.loads(s))
        film_source_list.append(film_source)
    return film_source_list

def get_collect_source_list() -> List[FilmSource]:
    """
    返回指定类型的采集Api信息 Master | Slave
    :param grade: 采集站等级
    :return: FilmSource对象列表
    """
    # 查询指定score范围的采集站点信息
    zl = redis_client.zrange(FILM_SOURCE_LIST_KEY, 0, -1)
    return get_collect_source(zl)

# FindCollectSourceById 通过Id标识获取对应的资源站信息
def FindCollectSourceById(id: str) -> FilmSource:
    for v in get_collect_source_list():
        if v.id == id:
            return v
    return None

def find_collect_source_by_id(id: str) -> FilmSource:
    for v in get_collect_source_list():
        if v.id == id:
            return v
    return None

def get_collect_source_list_by_grade(grade: SourceGrade) -> List[FilmSource]:
    """
    返回指定类型的采集Api信息 Master | Slave
    :param grade: 采集站等级
    :return: FilmSource对象列表
    """

    # 将grade转换为字符串作为score范围
    score = str(grade.value)
    # 查询指定score范围的采集站点信息
    zl = redis_client.zrangebyscore(FILM_SOURCE_LIST_KEY, min=score, max=score)
    return get_collect_source(zl)


def add_collect_source(film_source: FilmSource) -> (bool, str):
    """
    添加采集站信息，若已存在则返回错误
    """
    for v in get_collect_source_list():
        if v.uri == film_source.uri:
            return False, "当前采集站点信息已存在, 请勿重复添加"
    # 生成唯一ID
    film_source.id = generate_salt()
    data = film_source.model_dump_json()
    redis_client.zadd(FILM_SOURCE_LIST_KEY, {data: int(film_source.grade.value)})
    return True, "添加成功"

def del_collect_resource(id: str) -> bool:
    """
    通过Id删除对应的采集站点信息
    """
    for v in get_collect_source_list():
        if v.id == id:
            data = v.model_dump_json()
            redis_client.zrem(FILM_SOURCE_LIST_KEY, data)
            return True
    return False

def clear_all_collect_source():
    """
    删除所有采集站信息
    """
    redis_client.delete(FILM_SOURCE_LIST_KEY)

def exist_collect_source_list() -> bool:
    """
    查询是否已经存在站点list相关数据
    """
    return redis_client.exists(FILM_SOURCE_LIST_KEY) != 0


def save_collect_source_list(source_list: List[FilmSource]) -> bool:
    """
    保存采集站Api列表到Redis ZSet
    :param source_list: FilmSource对象列表
    :return: 是否成功
    """
    mapping = {}
    for source in source_list:
        # 将FilmSource对象转换为字典，然后序列化为JSON字符串
        data = json.dumps(source.__dict__, ensure_ascii=False)
        # Redis ZAdd 需要一个字典 {member: score}
        mapping[data] = int(source.grade.value)
    
    if not mapping:
        # 如果列表为空，可能需要清空或不做任何操作，这里选择清空以匹配Go的逻辑（如果传入空列表）
        # Go的ZAdd传入空列表不会报错，但不会添加任何成员。如果需要清空，需要显式调用delete。
        # 考虑到FilmSourceInit的调用场景，传入的列表通常不为空，这里不处理空列表清空逻辑。
        return True # 或者根据需求返回False或抛出异常

    try:
        # 使用 mapping 参数传递给 zadd
        redis_client.zadd(FILM_SOURCE_LIST_KEY, mapping=mapping)
        return True
    except Exception as e:
        print(f"保存采集站列表到Redis失败: {e}")
        return False


def update_collect_source(film_source: FilmSource) -> bool:
    for v in get_collect_source_list():
        if v.id != film_source.id and v.uri == film_source.uri:
            return False, "当前采集站链接已存在其他站点中, 请勿重复添加"
        elif v.id == film_source.id:
            # 删除当前旧的采集信息
            del_collect_resource(film_source.id)
            # 将新的采集信息存入list中
            data = film_source.model_dump_json()
            redis_client.zadd(FILM_SOURCE_LIST_KEY, {data: int(film_source.grade.value)})
    return True, ""
