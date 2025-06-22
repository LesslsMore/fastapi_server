import logging
from typing import List
import json

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import select

from model.collect.collect_source import FilmSource, SourceGrade, FilmSourceModel
from plugin.common.util.string_util import generate_salt
from plugin.db import redis_client, get_session
from config.data_config import FILM_SOURCE_LIST_KEY


class FilmSourceService:

    @staticmethod
    def get_collect_source_list() -> List[FilmSource]:
        """
        返回指定类型的采集Api信息 Master | Slave
        :param grade: 采集站等级
        :return: FilmSource对象列表
        """
        # 查询指定score范围的采集站点信息
        with get_session() as session:
            statement = select(FilmSourceModel).order_by(FilmSourceModel.name.desc())
            results = session.exec(statement).all()
            return results

    @staticmethod
    def find_collect_source_by_id(id: str) -> FilmSource:
        with get_session() as session:
            statement = select(FilmSourceModel).where(FilmSourceModel.id == id)
            results = session.exec(statement).one_or_none()
            return results

    @staticmethod
    def get_collect_source_list_by_grade(grade: SourceGrade) -> List[FilmSource]:
        """
        返回指定类型的采集Api信息 Master | Slave
        :param grade: 采集站等级
        :return: FilmSource对象列表
        """
        # 将grade转换为字符串作为score范围
        # score = str(grade.value)
        with get_session() as session:
            statement = select(FilmSourceModel).where(FilmSourceModel.grade == grade)
            results = session.exec(statement).all()
            return results

    @staticmethod
    def add_collect_source(film_source: FilmSource) -> (bool, str):
        """
        添加采集站信息，若已存在则返回错误
        """
        with get_session() as session:
            values = film_source.model_dump()
            stmt = insert(FilmSourceModel).values(**values)
            update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "id"}
            stmt = stmt.on_conflict_do_update(index_elements=[FilmSourceModel.id], set_=update_dict)
            session.exec(stmt)
            session.commit()
            return True, "添加成功"
        return False, "当前采集站链接已存在其他站点中, 请勿重复添加"

    @staticmethod
    def del_collect_resource(id: str) -> bool:
        """
        通过Id删除对应的采集站点信息
        """
        with get_session() as session:
            stat = delete(FilmSourceModel).where(FilmSourceModel.id == id)
            session.exec(stat)
            session.commit()
            return True
        return False

    @classmethod
    def exist_collect_source_list(cls) -> bool:
        """
        查询是否已经存在站点list相关数据
        """
        items = cls.get_collect_source_list()
        return len(items) > 0

    @staticmethod
    def save_collect_source_list(source_list: List[FilmSource]) -> bool:
        """
        保存采集站Api列表到Redis ZSet
        :param source_list: FilmSource对象列表
        :return: 是否成功
        """
        with get_session() as session:
            if not source_list:
                return
            table = FilmSourceModel.__table__
            data = [d.dict() if hasattr(d, 'dict') else d.__dict__ for d in source_list]
            stmt = insert(table).values(data)
            update_dict = {c.name: getattr(stmt.excluded, c.name) for c in table.columns if c.name != 'id'}
            stmt = stmt.on_conflict_do_update(index_elements=['id'], set_=update_dict)
            session.execute(stmt)
            session.commit()
            return True
        return False

    @classmethod
    def update_collect_source(cls, film_source: FilmSource) -> bool:
        return cls.add_collect_source(film_source)


def get_collect_source(film_source_json_list: List[str]) -> List[FilmSource]:
    """
    将字符串列表转换为FilmSource对象列表
    :param film_source_json_list: 字符串列表
    :return: FilmSource对象列表
    """
    film_source_list = []
    for film_source_json in film_source_json_list:
        film_source = FilmSource(**json.loads(film_source_json))
        film_source_list.append(film_source)
    return film_source_list


def get_collect_source_list() -> List[FilmSource]:
    """
    返回指定类型的采集Api信息 Master | Slave
    :param grade: 采集站等级
    :return: FilmSource对象列表
    """
    # 查询指定score范围的采集站点信息
    film_source_json_list = redis_client.zrange(FILM_SOURCE_LIST_KEY, 0, -1)
    return get_collect_source(film_source_json_list)


# FindCollectSourceById 通过Id标识获取对应的资源站信息
def find_collect_source_by_id(id: str) -> FilmSource:
    for film_source in get_collect_source_list():
        if film_source.id == id:
            return film_source
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
    film_source_json_list = redis_client.zrangebyscore(FILM_SOURCE_LIST_KEY, min=score, max=score)
    return get_collect_source(film_source_json_list)


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
        return True  # 或者根据需求返回False或抛出异常

    try:
        # 使用 mapping 参数传递给 zadd
        redis_client.zadd(FILM_SOURCE_LIST_KEY, mapping=mapping)
        return True
    except Exception as e:
        logging.info(f"保存采集站列表到Redis失败: {e}")
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
