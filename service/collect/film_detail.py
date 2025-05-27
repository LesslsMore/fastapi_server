from sqlalchemy import text

from model.system.movies import MovieDetail, MovieDescriptor, MovieUrlInfo

from typing import List
from model.collect.film_detail import FilmDetail
from plugin.db import pg_engine
from config.privide_config import ORIGINAL_FILM_DETAIL_KEY, RESOURCE_EXPIRED
from plugin.db import get_session, redis_client
from typing import Optional
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, SQLModel


# 批量保存原始影片详情数据到MySQL（伪实现，需结合ORM完善）
def batch_save_film_detail(film_detail: List[FilmDetail]):
    session = get_session()
    if not film_detail:
        return
    table = FilmDetail.__table__
    data = [d.dict() if hasattr(d, 'dict') else d.__dict__ for d in film_detail]
    stmt = insert(table).values(data)
    update_dict = {c.name: getattr(stmt.excluded, c.name) for c in table.columns if c.name != 'vod_id'}
    stmt = stmt.on_conflict_do_update(index_elements=['vod_id'], set_=update_dict)
    session.execute(stmt)
    session.commit()

# 保存未处理的完整影片详情信息到redis
def save_original_detail(fd: FilmDetail):
    data = fd.json(ensure_ascii=False)
    # redis = redis_client or init_redis_conn()
    redis_client.set(ORIGINAL_FILM_DETAIL_KEY % (fd.vod_id), data, ex=RESOURCE_EXPIRED)

# 保存未处理的完整影片详情信息到mysql（伪实现）
def save_original_detail2mysql(fd: FilmDetail):
    session = get_session()
    # 假设 FilmDetail 已继承 SQLModel 并映射表结构，否则需补充
    session.bulk_save_objects(fd)
    session.commit()

# 根据ID获取原始影片详情数据
def get_original_detail_by_id(id: int) -> Optional[FilmDetail]:
    data = redis_client.get(ORIGINAL_FILM_DETAIL_KEY % (id))
    if not data:
        return None
    try:
        fd = FilmDetail.parse_raw(data)
        return fd
    except Exception:
        return None


def convert_film_details(film_detail_list: List[FilmDetail]) -> List[MovieDetail]:
    return [convert_film_detail(film_detail) for film_detail in film_detail_list]


def convert_film_detail(film_detail: FilmDetail) -> MovieDetail:
    movie_detail = MovieDetail(
        id=film_detail.vod_id,
        cid=film_detail.type_id,
        pid=film_detail.type_id_1,
        name=film_detail.vod_name,
        picture=film_detail.vod_pic,
        DownFrom=film_detail.vod_down_from,
        descriptor=MovieDescriptor(
            subTitle=film_detail.vod_sub,
            cName=film_detail.type_name if hasattr(film_detail, 'type_name') else None,
            enName=film_detail.vod_en,
            initial=film_detail.vod_letter,
            classTag=film_detail.vod_class,
            actor=film_detail.vod_actor,
            director=film_detail.vod_director,
            writer=film_detail.vod_writer,
            blurb=film_detail.vod_blurb,
            remarks=film_detail.vod_remarks,
            releaseDate=film_detail.vod_pub_date,
            area=film_detail.vod_area,
            language=film_detail.vod_lang,
            year=film_detail.vod_year,
            state=film_detail.vod_state,
            updateTime=film_detail.vod_time,
            addTime=film_detail.vod_time_add,
            dbId=film_detail.vod_douban_id,
            dbScore=film_detail.vod_douban_score,
            hits=film_detail.vod_hits,
            content=film_detail.vod_content,
        ),
        playFrom=film_detail.vod_play_from.split(film_detail.vod_play_note) if film_detail.vod_play_from and film_detail.vod_play_note else None,
        playList=gen_film_play_list(film_detail.vod_play_url, film_detail.vod_play_note),
        downloadList=gen_film_play_list(film_detail.vod_down_url, film_detail.vod_play_note),
    )
    return movie_detail


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


def exist_film_detail_table() -> bool:
    """
    判断是否存在FilmDetail Table
    """
    session = get_session()
    result = session.execute(text("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'film_detail'
    )
    """)).fetchone()
    return result[0]


