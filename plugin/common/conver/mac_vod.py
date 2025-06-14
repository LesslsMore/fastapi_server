import logging
import re
from datetime import datetime

from dao.collect.MacVodDao import gen_film_play_list
from model.system.movies import MovieDetail, MovieDescriptor, MovieBasicInfo
from typing import List
from model.collect.MacVod import MacVod
from model.system.search import SearchInfo


def mac_vod_list_to_movie_detail_list(mac_vod_list: List[MacVod]) -> List[MovieDetail]:
    return [mac_vod_to_movie_detail(mac_vod) for mac_vod in mac_vod_list]


def movie_detail_list_to_search_info_list(movie_detail_list: List[MovieDetail]) -> List[SearchInfo]:
    return [movie_detail_to_search_info(movie_detail) for movie_detail in movie_detail_list]


def mac_vod_list_to_search_info_list(mac_vod_list: List[MacVod]) -> List[SearchInfo]:
    search_info_list = []

    for mac_vod in mac_vod_list:
        movie_detail = mac_vod_to_movie_detail(mac_vod)
        search_info = movie_detail_to_search_info(movie_detail)
        search_info_list.append(search_info)

    return search_info_list


def mac_vod_list_to_movie_basic_info_list(mac_vod_list: List[MacVod]) -> List[MovieBasicInfo]:
    movie_basic_info_list = []

    for mac_vod in mac_vod_list:
        movie_detail = mac_vod_to_movie_detail(mac_vod)
        movie_basic_info = movie_detail_to_movie_basic_info(movie_detail)
        movie_basic_info_list.append(movie_basic_info)

    return movie_basic_info_list


def movie_detail_to_search_info(detail: MovieDetail) -> SearchInfo:
    score = float(detail.descriptor.dbScore) if detail.descriptor.dbScore else 0.0
    stamp = datetime.strptime(detail.descriptor.updateTime, "%Y-%m-%d %H:%M:%S").timestamp()
    year = int(detail.descriptor.year) if detail.descriptor.year else 0
    try:
        year_match = re.search(r"[1-9][0-9]{3}", detail.descriptor.releaseDate)
        year = int(year_match.group()) if year_match else 0
    except Exception as e:
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


def movie_detail_to_movie_basic_info(movie_detail):
    movie_basic_info = MovieBasicInfo(
        id=movie_detail.id,
        cid=movie_detail.cid,
        pid=movie_detail.pid,
        name=movie_detail.name,
        sub_title=movie_detail.descriptor.subTitle,
        c_name=movie_detail.descriptor.cName,
        state=movie_detail.descriptor.state,
        picture=movie_detail.picture,
        actor=movie_detail.descriptor.actor,
        director=movie_detail.descriptor.director,
        blurb=movie_detail.descriptor.blurb,
        remarks=movie_detail.descriptor.remarks,
        area=movie_detail.descriptor.area,
        year=movie_detail.descriptor.year
    )
    return movie_basic_info


def mac_vod_to_movie_detail(film_detail: MacVod) -> MovieDetail:
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
        playFrom=film_detail.vod_play_from.split(
            film_detail.vod_play_note) if film_detail.vod_play_from and film_detail.vod_play_note else None,
        playList=gen_film_play_list(film_detail.vod_play_url, film_detail.vod_play_note),
        downloadList=gen_film_play_list(film_detail.vod_down_url, film_detail.vod_play_note),
    )
    return movie_detail
