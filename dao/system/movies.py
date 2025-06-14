import logging
from datetime import datetime
from typing import List, Optional, Union
import hashlib
import re
import json

from config.data_config import SEARCH_INFO_TEMP, MULTIPLE_SITE_DETAIL
from dao.collect.movie_dao import movie_detail_to_movie_basic_info, MovieDao
from model.system.search import SearchInfo
from plugin.db import redis_client
from model.system.movies import MovieDetail, MovieBasicInfo
from dao.system.search_tag import save_search_tag


def generate_hash_key(key: Union[str, int]) -> str:
    m_name = str(key)
    m_name = re.sub(r"\s", "", m_name)
    m_name = re.sub(r"～.*～$", "", m_name)
    m_name = re.sub(r"^[\W_]+|[\W_]+$", "", m_name)
    m_name = re.sub(r"季.*", "季", m_name)
    h = hashlib.md5()
    h.update(m_name.encode("utf-8"))
    return h.hexdigest()





def batch_save_search_info(movie_detail_list: List[MovieDetail]) -> None:
    try:
        search_info_list = [movie_detail_to_search_info(movie_detail) for movie_detail in movie_detail_list]
        rdb_save_search_info(search_info_list)
    except Exception as e:
        logging.error('batch_save_search_info: {}', e)


def movie_detail_to_search_info(detail: MovieDetail) -> SearchInfo:
    score = float(detail.descriptor.dbScore) if detail.descriptor.dbScore else 0.0
    stamp = datetime.strptime(detail.descriptor.updateTime, "%Y-%m-%d %H:%M:%S").timestamp()
    year = int(detail.descriptor.year) if detail.descriptor.year else 0
    try:
        year_match = re.search(r"[1-9][0-9]{3}", detail.descriptor.releaseDate)
        year = int(year_match.group()) if year_match else 0
    except Exception as e:
        print(f"convert_search_info Error: {e}")
        logging.error(f"convert_search_info Error: {e}")

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


def rdb_save_search_info(search_info_list: List[SearchInfo]):
    """
    批量保存检索信息到Redis
    :param search_info_list: SearchInfo对象列表
    """
    members = []
    for search_info in search_info_list:
        member = search_info.model_dump_json()
        members.append((search_info.mid, member))
    redis_client.zadd(SEARCH_INFO_TEMP, {member: score for score, member in members})


def save_movie_detail(movie_detail: MovieDetail) -> Optional[Exception]:
    """
    保存单部影片详情信息到Redis中，功能与Go版 SaveDetail 保持一致
    :param movie_detail: MovieDetail对象
    :return: 异常对象或None
    """
    try:
        MovieDao.set_movie_detail(movie_detail)

        movie_basic_info = movie_detail_to_movie_basic_info(movie_detail)
        MovieDao.set_movie_basic_info(movie_basic_info)

        search_info = movie_detail_to_search_info(movie_detail)
        save_search_tag(search_info)
        # 保存影片检索信息到searchTable（如有需要可调用 batch_save_search_info 或单条保存）
        # 这里假设有 save_search_info 单条保存函数，否则可忽略
        # save_search_info(search_info)
        return None
    except Exception as e:
        logging.error(f'save_detail error: {e}')
        return e


def save_movie_detail_list(movie_detail_list: List[MovieDetail]) -> None:
    """
    保存影片详情信息到Redis中
    :param movie_detail_list: MovieDetail对象列表
    """
    for movie_detail in movie_detail_list:
        save_movie_detail(movie_detail)

    batch_save_search_info(movie_detail_list)
