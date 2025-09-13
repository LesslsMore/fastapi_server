from anime.anime_vod import anime_vod_dao


def test_query():
    name = '拔作岛'
    anime_vod = anime_vod_dao.query(filter_dict={"vod_name": name})
    print(anime_vod)

def test_paginate():

    anime_vod = anime_vod_dao.paginate()
    print(anime_vod)