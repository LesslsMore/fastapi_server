from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import hashlib
import re
import json

from config.data_config import SEARCH_INFO_TEMP, MOVIE_BASIC_INFO_KEY, MOVIE_DETAIL_KEY, MULTIPLE_SITE_DETAIL, \
    FILM_EXPIRED
from model.service.search import save_search_tag
from model.system.search import SearchInfo
from plugin.db import redis_client, init_redis_conn, get_redis_client
from model.system.movies import MovieDetail, MovieBasicInfo, MovieDescriptor, MovieUrlInfo


def generate_hash_key(key: Union[str, int]) -> str:
    m_name = str(key)
    m_name = re.sub(r"\s", "", m_name)
    m_name = re.sub(r"～.*～$", "", m_name)
    m_name = re.sub(r"^[\W_]+|[\W_]+$", "", m_name)
    m_name = re.sub(r"季.*", "季", m_name)
    h = hashlib.md5()
    h.update(m_name.encode("utf-8"))
    return h.hexdigest()


def save_details(list_: List[MovieDetail]) -> None:
    """
    保存影片详情信息到Redis中
    :param list_: MovieDetail对象列表
    """
    redis_client = get_redis_client() or init_redis_conn()
    for detail in list_:
        key = MOVIE_DETAIL_KEY % (detail.cid, detail.id)
        redis_client.set(key, detail.json(), ex=FILM_EXPIRED)
        save_movie_basic_info(detail)
        search_info = convert_search_info(detail)
        save_search_tag(search_info)
    batch_save_search_info(list_)


def save_movie_basic_info(detail: MovieDetail):
    basic = MovieBasicInfo(
        id=detail.id,
        cid=detail.cid,
        pid=detail.pid,
        name=detail.name,
        sub_title=detail.descriptor.subTitle,
        c_name=detail.descriptor.cName,
        state=detail.descriptor.state,
        picture=detail.picture,
        actor=detail.descriptor.actor,
        director=detail.descriptor.director,
        blurb=detail.descriptor.blurb,
        remarks=detail.descriptor.remarks,
        area=detail.descriptor.area,
        year=detail.descriptor.year
    )
    key = MOVIE_BASIC_INFO_KEY % (detail.cid, detail.id)
    redis_client = get_redis_client() or init_redis_conn()
    redis_client.set(key, basic.json(), ex=FILM_EXPIRED)


def get_basic_info_by_key(key: str) -> Optional[MovieBasicInfo]:
    redis = redis_client or init_redis_conn()
    data = redis.get(key)
    if data:
        #     	// 执行本地图片匹配
        # ReplaceBasicDetailPic(&basic)
        return MovieBasicInfo.parse_raw(data)
    return None


def get_detail_by_key(key: str) -> Optional[MovieDetail]:
    redis = redis_client or init_redis_conn()
    data = redis.get(key)
    if data:
        return MovieDetail.parse_raw(data)
    return None


def save_site_play_list(site_id: str, details: List[MovieDetail]):
    redis_client = get_redis_client() or init_redis_conn()
    res = {}
    for d in details:
        if d.playList and len(d.playList) > 0:
            data = json.dumps([item.dict() for item in d.playList[0]])
            if d.descriptor.cName and "解说" in d.descriptor.cName:
                continue
            if d.descriptor.dbId:
                res[generate_hash_key(d.descriptor.dbId)] = data
            res[generate_hash_key(d.name)] = data
    if res:
        redis_client.hmset(MULTIPLE_SITE_DETAIL % site_id, res)


def batch_save_search_info(details: List[MovieDetail]) -> None:
    info_list = [convert_search_info(detail) for detail in details]
    rdb_save_search_info(info_list)

def convert_search_info(detail: MovieDetail) -> SearchInfo:
    score = float(detail.descriptor.dbScore) if detail.descriptor.dbScore else 0.0
    stamp = datetime.strptime(detail.descriptor.updateTime, "%Y-%m-%d %H:%M:%S").timestamp()
    year = int(detail.descriptor.year) if detail.descriptor.year else 0
    try:
        year_match = re.search(r"[1-9][0-9]{3}", detail.descriptor.releaseDate)
        year = int(year_match.group()) if year_match else 0
    except Exception as e:
        print(f"SaveDetails Error: {e}")

    return SearchInfo(
        mid=detail.id,
        cid=detail.cid,
        pid=detail.pid,
        name=detail.name,
        sub_title=detail.descriptor.subTitle,
        c_name=detail.descriptor.cName,
        class_tag=detail.descriptor.classTag,
        area=detail.descriptor.area,
        language=detail.descriptor.language,
        year=year,
        initial=detail.descriptor.initial,
        score=score,
        hits=detail.descriptor.hits,
        update_stamp=int(stamp),
        state=detail.descriptor.state,
        remarks=detail.descriptor.remarks,
        release_stamp=detail.descriptor.addTime
    )




def rdb_save_search_info(list: List[SearchInfo]):
    """
    批量保存检索信息到Redis
    :param list: SearchInfo对象列表
    """
    redis_client = get_redis_client() or init_redis_conn()
    members = []
    for s in list:
        member = s.model_dump_json()
        members.append((s.mid, member))
    redis_client.zadd(SEARCH_INFO_TEMP, {member: score for score, member in members})
