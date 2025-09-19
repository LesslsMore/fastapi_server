from typing import List, Tuple

from sqlalchemy import text, func
from sqlmodel import select

from demo.sql import get_session
from model.collect.MacVod import MacVod
from model.system.movies import MovieUrlInfo


class MacVodDao:

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
                    text('''UNNEST(
                    STRING_TO_ARRAY(
                        regexp_replace(vod_class, '[\\、\\/\s，]+', ',', 'g'),
                        ','
                    )
                    ) AS tag'''),
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


def convert_play_url(play_url: str) -> List[MovieUrlInfo]:
    l = []
    for p in play_url.split('#'):
        if '$' in p:
            episode, link = p.split('$', 1)
            l.append(MovieUrlInfo(episode=episode, link=link))
        else:
            l.append(MovieUrlInfo(episode="(｀・ω・´)", link=p))
    return l
