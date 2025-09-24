from typing import Optional, List

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field

from dao.base_dao import BaseDao
from model.system.movies import MovieDetail, MovieBasicInfo, MovieUrlInfo, MovieDescriptor


class MovieDetailModel(SQLModel, MovieDetail):
    __tablename__ = 'movie_detail'
    id: int = Field(primary_key=True)
    playFrom: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSONB))
    playList: Optional[List[List[MovieUrlInfo]]] = Field(default_factory=list, sa_column=Column(JSONB))
    downloadList: Optional[List[List[MovieUrlInfo]]] = Field(default_factory=list, sa_column=Column(JSONB))
    descriptor: Optional[MovieDescriptor] = Field(default=None, sa_column=Column(JSONB))


class MovieBasicInfoModel(SQLModel, MovieBasicInfo):
    __tablename__ = 'movie_basic_info'
    id: int = Field(primary_key=True)


movie_basic_info_dao = BaseDao(MovieBasicInfoModel)
movie_detail_dao = BaseDao(MovieDetailModel)
