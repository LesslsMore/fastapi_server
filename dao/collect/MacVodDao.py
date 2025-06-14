
from sqlalchemy import text, func

from model.system.movies import MovieUrlInfo
from typing import List, Tuple
from model.collect.MacVod import MacVod
from config.privide_config import ORIGINAL_FILM_DETAIL_KEY, RESOURCE_EXPIRED
from plugin.db import get_session, redis_client
from typing import Optional
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import select


class MacVodDao:
    @staticmethod
    # 批量保存原始影片详情数据到MySQL（伪实现，需结合ORM完善）
    def batch_save_film_detail(film_detail_list: List[MacVod]):
        session = get_session()
        if not film_detail_list:
            return
        table = MacVod.__table__
        data = [d.dict() if hasattr(d, 'dict') else d.__dict__ for d in film_detail_list]
        stmt = insert(table).values(data)
        update_dict = {c.name: getattr(stmt.excluded, c.name) for c in table.columns if c.name != 'vod_id'}
        stmt = stmt.on_conflict_do_update(index_elements=['vod_id'], set_=update_dict)
        session.execute(stmt)
        session.commit()

    @staticmethod
    def select_mac_vod(vod_id: int):
        with get_session() as session:
            statement = select(MacVod).where(MacVod.vod_id == vod_id)
            results = session.exec(statement)
            item = results.first()
            return item

    @staticmethod
    def count_vod_class_tags(type_id_1: int) -> List[Tuple[str, int]]:
        """
        统计指定 type_id_1 的所有记录中 vod_class 各 tag 的出现次数。

        :param session: 数据库会话
        :param type_id_1: 用于筛选记录的一级分类ID
        :return: 返回 tag 及其出现次数的列表
        """
        with get_session() as session:
            statement = (
                select(
                    text("UNNEST(STRING_TO_ARRAY(vod_class, ',')) AS tag"),
                    func.count().label("count")
                )
                .where(
                    (MacVod.type_id_1 == type_id_1) &
                    (MacVod.vod_class.is_not(None))
                )
                .group_by(text("tag"))
                .order_by(text("count DESC"))
            )

            result = session.exec(statement).all()
            return [(row.count, row.tag) for row in result]

    @staticmethod
    def count_vod_key_tags(field_name, split, type_id_1: int) -> List[Tuple[str, int]]:
        """
        统计指定 type_id_1 的所有记录中 vod_class 各 tag 的出现次数（纯 SQL 实现）。

        :param session: 数据库会话
        :param type_id_1: 用于筛选记录的一级分类ID
        :return: 返回 tag 及其出现次数的列表
        """
        # 白名单校验防止 SQL 注入
        allowed_fields = {"vod_class", "vod_area", "vod_lang"}
        if field_name not in allowed_fields:
            raise ValueError(f"Invalid field name: {field_name}")
        with get_session() as session:
            query = text(f"""
                SELECT 
                    UNNEST(STRING_TO_ARRAY({field_name}, :split)) AS tag,
                    COUNT(*) AS count
                FROM 
                    mac_vod
                WHERE 
                    type_id_1 = :type_id_1
                    AND vod_class IS NOT NULL
                GROUP BY 
                    tag
                ORDER BY 
                    count DESC;
            """)

            result = session.execute(query, {"split": split, "type_id_1": type_id_1}).fetchall()
            return [(row[1], row[0]) for row in result]

    @staticmethod
    def select_mac_vod_list(vod_id_list: List[int]):
        with get_session() as session:
            # 构建批量查询语句
            statement = select(MacVod).where(
                MacVod.vod_id.in_(vod_id_list)  # 使用 IN 操作符匹配多个 ID
            )
            results = session.exec(statement)
            return results.all()  # 返回所有匹配结果的列表


# 保存未处理的完整影片详情信息到redis
def save_original_detail(fd: MacVod):
    data = fd.json(ensure_ascii=False)
    # redis = redis_client or init_redis_conn()
    redis_client.set(ORIGINAL_FILM_DETAIL_KEY % (fd.vod_id), data, ex=RESOURCE_EXPIRED)


# 保存未处理的完整影片详情信息到mysql（伪实现）
def save_original_detail2mysql(fd: MacVod):
    session = get_session()
    # 假设 FilmDetail 已继承 SQLModel 并映射表结构，否则需补充
    session.bulk_save_objects(fd)
    session.commit()


# 根据ID获取原始影片详情数据
def get_original_detail_by_id(id: int) -> Optional[MacVod]:
    data = redis_client.get(ORIGINAL_FILM_DETAIL_KEY % (id))
    if not data:
        return None
    try:
        fd = MacVod.parse_raw(data)
        return fd
    except Exception:
        return None


def gen_film_play_list(play_url: str, separator: str) -> List[List[MovieUrlInfo]]:
    res = []
    if separator:
        for l in play_url.split(separator):
            if ".m3u8" in l or ".mp4" in l:
                res.append(convert_play_url(l))
    else:
        if ".m3u8" in play_url or ".mp4" in play_url:
            res.append(convert_play_url(play_url))
    return res


def gen_all_film_play_list(play_url: str, separator: str) -> List[List[MovieUrlInfo]]:
    res = []
    if separator:
        for l in play_url.split(separator):
            res.append(convert_play_url(l))
        return res
    res.append(convert_play_url(play_url))
    return res


def convert_play_url(play_url: str) -> List[MovieUrlInfo]:
    l = []
    for p in play_url.split('#'):
        if '$' in p:
            episode, link = p.split('$', 1)
            l.append(MovieUrlInfo(episode=episode, link=link))
        else:
            l.append(MovieUrlInfo(episode="(｀・ω・´)", link=p))
    return l
