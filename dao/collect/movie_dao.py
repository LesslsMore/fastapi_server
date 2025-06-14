from sqlalchemy.dialects.postgresql import insert
from model.collect.movie_entity import MovieDetailModel, MovieBasicInfoModel
from model.system.movies import MovieBasicInfo, MovieDetail
from plugin.db import redis_client, get_session





class MovieDao:
    @staticmethod
    def upsert_movie_basic_info(movie_basic_info: MovieBasicInfo):
        with get_session() as session:
            values = movie_basic_info.model_dump()
            stmt = insert(MovieBasicInfoModel).values(**values)
            update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "id"}
            stmt = stmt.on_conflict_do_update(index_elements=[MovieBasicInfoModel.id], set_=update_dict)
            session.exec(stmt)
            session.commit()

    # @staticmethod
    # def select_movie_basic_info(search_info: SearchInfo):
    #     with get_session() as session:
    #         statement = select(MovieBasicInfoModel).where(MovieBasicInfoModel.id == search_info.mid)
    #         results = session.exec(statement)
    #         item = results.first()
    #         return item
    #
    # @staticmethod
    # def select_movie_basic_info_list(mids: List[int]):
    #     with get_session() as session:
    #         # 构建批量查询语句
    #         statement = select(MovieBasicInfoModel).where(
    #             MovieBasicInfoModel.id.in_(mids)  # 使用 IN 操作符匹配多个 ID
    #         )
    #         results = session.exec(statement)
    #         return results.all()  # 返回所有匹配结果的列表

    @staticmethod
    def set_movie_basic_info(movie_basic_info: MovieBasicInfo):
        MovieDao.upsert_movie_basic_info(movie_basic_info)

    @staticmethod
    def upsert_movie_detail(movie_detail: MovieDetail):
        with get_session() as session:
            values = movie_detail.model_dump()
            stmt = insert(MovieDetailModel).values(**values)
            update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "id"}
            stmt = stmt.on_conflict_do_update(index_elements=[MovieDetailModel.id], set_=update_dict)
            session.exec(stmt)
            session.commit()

    # @staticmethod
    # def select_movie_detail(vod_id: int):
    #     with get_session() as session:
    #         statement = select(MovieDetailModel).where(MovieDetailModel.id == vod_id)
    #         results = session.exec(statement)
    #         movie_detail = results.first()
    #         return movie_detail

    @staticmethod
    def set_movie_detail(movie_detail: MovieDetail):
        MovieDao.upsert_movie_detail(movie_detail)

    # @staticmethod
    # def get_movie_detail(vod_id: int):
    #     movie_detail_model = MovieDao.select_movie_detail(vod_id)
    #     if movie_detail_model:
    #         movie_detail = MovieDetail(**movie_detail_model.model_dump())
    #         return movie_detail
    #     return None
