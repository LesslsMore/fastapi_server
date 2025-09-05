import hashlib
import logging
import re
from typing import List, Optional, Union

from config.data_config import SEARCH_INFO_TEMP
from dao.system.search_tag import save_search_tag
from model.collect.movie_entity import movie_detail_dao, movie_basic_info_dao
from model.system.movies import MovieDetail
from model.system.search import SearchInfo
from plugin.common.conver.mac_vod import movie_detail_list_to_search_info_list, movie_detail_to_movie_basic_info, \
    movie_detail_to_search_info
from plugin.db import redis_client


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
        search_info_list = movie_detail_list_to_search_info_list(movie_detail_list)
        rdb_save_search_info(search_info_list)
    except Exception as e:
        logging.error('batch_save_search_info: {}', e)


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
        movie_detail_dao.upsert(movie_detail)

        movie_basic_info = movie_detail_to_movie_basic_info(movie_detail)
        movie_basic_info_dao.upsert(movie_basic_info)

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
