from typing import Optional, List

from sqlmodel import select
from sqlalchemy.dialects.postgresql import insert

from config.data_config import MOVIE_BASIC_INFO_KEY, FILM_EXPIRED, MOVIE_DETAIL_KEY
from model.collect.movie_entity import MovieDetailModel, MovieBasicInfoModel
from model.system.movies import MovieBasicInfo, MovieDetail
from model.system.search import SearchInfo
from plugin.db import redis_client, get_session


def convert_movie_basic_info(movie_detail):
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


# def set_movie_basic_info(movie_basic_info: MovieBasicInfo):
#     key = MOVIE_BASIC_INFO_KEY % (movie_basic_info.cid, movie_basic_info.id)
#     redis_client.set(key, movie_basic_info.json(), ex=FILM_EXPIRED)
#
#
# def get_movie_basic_info(search_info: SearchInfo):
#     key = MOVIE_BASIC_INFO_KEY % (search_info.cid, search_info.mid)
#     data = redis_client.get(key)
#     if data:
#         movie_basic_info = MovieBasicInfo.parse_raw(data)
#         return movie_basic_info
#     return None

def upsert_movie_basic_info(movie_basic_info: MovieBasicInfo):
    with get_session() as session:
        values = movie_basic_info.model_dump()
        stmt = insert(MovieBasicInfoModel).values(**values)
        update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "id"}
        stmt = stmt.on_conflict_do_update(index_elements=[MovieBasicInfoModel.id], set_=update_dict)
        session.exec(stmt)
        session.commit()


def select_movie_basic_info(search_info: SearchInfo):
    with get_session() as session:
        statement = select(MovieBasicInfoModel).where(MovieBasicInfoModel.id == search_info.mid)
        results = session.exec(statement)
        item = results.first()
        return item

def select_movie_basic_info_list(search_info_list: List[SearchInfo]):
    mids = [search_info.mid for search_info in search_info_list]
    with get_session() as session:
        # 构建批量查询语句
        statement = select(MovieBasicInfoModel).where(
            MovieBasicInfoModel.id.in_(mids)  # 使用 IN 操作符匹配多个 ID
        )
        results = session.exec(statement)
        return results.all()  # 返回所有匹配结果的列表

def set_movie_basic_info(movie_basic_info: MovieBasicInfo):
    upsert_movie_basic_info(movie_basic_info)


def get_movie_basic_info(search_info: SearchInfo):
    # movie_detail = get_movie_detail(search_info)
    # if movie_detail:
    #     return convert_movie_basic_info(movie_detail)
    # return None

    movie_basic_info_model = select_movie_basic_info(search_info)
    if movie_basic_info_model:
        movie_basic_info = MovieBasicInfo(**movie_basic_info_model.model_dump())
        return movie_basic_info
    return None


def upsert_movie_detail(movie_detail: MovieDetail):
    with get_session() as session:
        values = movie_detail.model_dump()
        stmt = insert(MovieDetailModel).values(**values)
        update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "id"}
        stmt = stmt.on_conflict_do_update(index_elements=[MovieDetailModel.id], set_=update_dict)
        session.exec(stmt)
        session.commit()


def select_movie_detail(search_info: SearchInfo):
    with get_session() as session:
        statement = select(MovieDetailModel).where(MovieDetailModel.id == search_info.mid)
        results = session.exec(statement)
        movie_detail = results.first()
        return movie_detail


def set_movie_detail(movie_detail: MovieDetail):
    upsert_movie_detail(movie_detail)


def get_movie_detail(search_info: SearchInfo):
    movie_detail_model = select_movie_detail(search_info)
    if movie_detail_model:
        movie_detail = MovieDetail(**movie_detail_model.model_dump())
        return movie_detail
    return None

# def set_movie_detail(movie_detail: MovieDetail):
#     key = MOVIE_DETAIL_KEY % (movie_detail.cid, movie_detail.id)
#     redis_client.set(key, movie_detail.json(), ex=FILM_EXPIRED)
#
#
# def get_movie_detail(search_info: SearchInfo) -> Optional[MovieDetail]:
#     key = MOVIE_DETAIL_KEY % (search_info.cid, search_info.mid)
#     data = redis_client.get(key)
#     if data:
#         return MovieDetail.parse_raw(data)
#     return None
