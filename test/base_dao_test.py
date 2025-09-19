from anime.anime_vod import anime_vod_dao
from config.data_config import INDEX_CACHE_KEY
from dao.collect.kv_dao import KVDao
from dao.system.search import get_hot_movie_by_pid
from model.system.response import Page


def test_query():
    name = '拔作岛'
    anime_vod = anime_vod_dao.query_item(filter_dict={"vod_name": name})
    print(anime_vod)
    # assert anime_vod is not None

def test_paginate():

    anime_vod = anime_vod_dao.paginate()
    print(anime_vod)

def test_page():
    page = Page(pageSize=14, current=1)
    cid = 4
    hot_movies = get_hot_movie_by_pid(cid, page)
    print(hot_movies)

def test_delete():
    res = KVDao.delete_key(INDEX_CACHE_KEY)
    print(res)