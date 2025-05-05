from typing import List, Optional, Dict, Any, Union
import hashlib
import re
import json
from model.system.search import SearchInfo
from plugin.db.redis_client import redis_client, init_redis_conn
from model.system.movies import MovieDetail, MovieBasicInfo, MovieDescriptor, MovieUrlInfo

# Redis Key 配置
MOVIE_DETAIL_KEY = "MovieDetail:Cid%d:Id%d"
MOVIE_BASIC_INFO_KEY = "MovieBasicInfo:Cid%d:Id%d"
MULTIPLE_SITE_DETAIL = "MultipleSource:%s"
FILM_EXPIRED = 60 * 60 * 24 * 7  # 7天

def generate_hash_key(key: Union[str, int]) -> str:
    m_name = str(key)
    m_name = re.sub(r"\s", "", m_name)
    m_name = re.sub(r"～.*～$", "", m_name)
    m_name = re.sub(r"^[\W_]+|[\W_]+$", "", m_name)
    m_name = re.sub(r"季.*", "季", m_name)
    h = hashlib.md5()
    h.update(m_name.encode("utf-8"))
    return h.hexdigest()

def save_detail(detail: MovieDetail):
    key = MOVIE_DETAIL_KEY % (detail.cid, detail.id)
    redis_client.set(key, detail.json(), ex=FILM_EXPIRED)
    save_movie_basic_info(detail)

def save_details(details: List[MovieDetail]):
    for detail in details:
        save_detail(detail)

def save_movie_basic_info(detail: MovieDetail):
    basic = MovieBasicInfo(
        id=detail.id,
        cid=detail.cid,
        pid=detail.pid,
        name=detail.name,
        sub_title=detail.sub_title,
        c_name=detail.c_name,
        state=detail.state,
        picture=detail.picture,
        actor=getattr(detail, "actor", None),
        director=getattr(detail, "director", None),
        blurb=getattr(detail, "blurb", None),
        remarks=detail.remarks,
        area=detail.area,
        year=detail.year
    )
    key = MOVIE_BASIC_INFO_KEY % (detail.cid, detail.id)
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
    res = {}
    for d in details:
        if d.play_list and len(d.play_list) > 0:
            data = json.dumps([item.dict() for item in d.play_list[0]])
            if d.c_name and "解说" in d.c_name:
                continue
            if d.db_id:
                res[generate_hash_key(d.db_id)] = data
            res[generate_hash_key(d.name)] = data
    if res:
        redis_client.hmset(MULTIPLE_SITE_DETAIL % site_id, res)

def batch_save_search_info(details: List[MovieDetail]):
    pass

def get_basic_info_by_search_infos(infos: List[SearchInfo]) -> List[MovieBasicInfo]:
    redis = redis_client or init_redis_conn()
    result = []
    for info in infos:
        key = MOVIE_BASIC_INFO_KEY % (info.cid, info.mid)
        data = redis.get(key)
        if data:
            basic = MovieBasicInfo.parse_raw(data)
            result.append(basic)
    return result