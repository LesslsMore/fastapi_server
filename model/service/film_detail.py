from sqlalchemy import text

from model.system.movies import MovieDetail, MovieDescriptor, MovieUrlInfo
from typing import List

import json
from typing import List, Optional
from model.system.film_detail import FilmDetail
from plugin.db.redis_client import redis_client, init_redis_conn, get_redis_client
from config.privide_config import ORIGINAL_FILM_DETAIL_KEY, RESOURCE_EXPIRED
from plugin.db.postgres import get_db
import requests
from typing import Dict, Any, Optional
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import SQLModel, Session
import logging

# 批量保存原始影片详情数据到MySQL（伪实现，需结合ORM完善）
def batch_save_original_detail(dl: List[FilmDetail]):
    session = get_db()
    if not dl:
        return
    table = FilmDetail.__table__
    data = [d.dict() if hasattr(d, 'dict') else d.__dict__ for d in dl]
    stmt = insert(table).values(data)
    update_dict = {c.name: getattr(stmt.excluded, c.name) for c in table.columns if c.name != 'vod_id'}
    stmt = stmt.on_conflict_do_update(index_elements=['vod_id'], set_=update_dict)
    session.execute(stmt)
    session.commit()

# 保存未处理的完整影片详情信息到redis
def save_original_detail(fd: FilmDetail):
    data = fd.json(ensure_ascii=False)
    # redis = redis_client or init_redis_conn()
    redis_client.set(ORIGINAL_FILM_DETAIL_KEY.format(fd.vod_id), data, ex=RESOURCE_EXPIRED)

# 保存未处理的完整影片详情信息到mysql（伪实现）
def save_original_detail2mysql(fd: FilmDetail):
    session = get_db()
    # 假设 FilmDetail 已继承 SQLModel 并映射表结构，否则需补充
    session.bulk_save_objects(fd)
    session.commit()

# 根据ID获取原始影片详情数据
def get_original_detail_by_id(id: int) -> Optional[FilmDetail]:
    redis = get_redis_client() or init_redis_conn()
    data = redis.get(ORIGINAL_FILM_DETAIL_KEY.format(id))
    if not data:
        return None
    try:
        fd = FilmDetail.parse_raw(data)
        return fd
    except Exception:
        return None


def convert_film_details(details: List[FilmDetail]) -> List[MovieDetail]:
    return [convert_film_detail(d) for d in details]


def convert_film_detail(detail: FilmDetail) -> MovieDetail:
    md = MovieDetail(
        id=detail.vod_id,
        cid=detail.type_id,
        pid=detail.type_id_1,
        name=detail.vod_name,
        picture=detail.vod_pic,
        DownFrom=detail.vod_down_from,
        descriptor=MovieDescriptor(
            subTitle=detail.vod_sub,
            cName=detail.type_name if hasattr(detail, 'type_name') else None,
            enName=detail.vod_en,
            initial=detail.vod_letter,
            classTag=detail.vod_class,
            actor=detail.vod_actor,
            director=detail.vod_director,
            writer=detail.vod_writer,
            blurb=detail.vod_blurb,
            remarks=detail.vod_remarks,
            releaseDate=detail.vod_pub_date,
            area=detail.vod_area,
            language=detail.vod_lang,
            year=detail.vod_year,
            state=detail.vod_state,
            updateTime=detail.vod_time,
            addTime=detail.vod_time_add,
            dbId=detail.vod_douban_id,
            dbScore=detail.vod_douban_score,
            hits=detail.vod_hits,
            content=detail.vod_content,
        ),
        playFrom=detail.vod_play_from.split(detail.vod_play_note) if detail.vod_play_from and detail.vod_play_note else None,
        playList=gen_film_play_list(detail.vod_play_url, detail.vod_play_note),
        downloadList=gen_film_play_list(detail.vod_down_url, detail.vod_play_note),
    )
    return md


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



def create_film_detail_table():
    """
    创建存储影片详情的数据表
    """
    session = get_db()
    FilmDetail.metadata.create_all(session.get_bind())


def exist_film_detail_table(session: Session) -> bool:
    """
    判断是否存在FilmDetail Table
    """
    result = session.execute(text("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'film_detail'
    )
    """)).fetchone()
    return result[0]


