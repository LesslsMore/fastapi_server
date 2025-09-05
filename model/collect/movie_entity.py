from typing import Optional, List

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field

from dao.base_dao import BaseDao
from model.system.movies import MovieDetail, MovieBasicInfo, MovieUrlInfo, MovieDescriptor


class MovieDetailModel(SQLModel, MovieDetail):
    __tablename__ = 'movie_detail'
    id: int = Field(primary_key=True)
    playFrom: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    playList: Optional[List[List[MovieUrlInfo]]] = Field(default_factory=list, sa_column=Column(JSON))
    downloadList: Optional[List[List[MovieUrlInfo]]] = Field(default_factory=list, sa_column=Column(JSON))
    descriptor: Optional[MovieDescriptor] = Field(default=None, sa_column=Column(JSON))


class MovieBasicInfoModel(SQLModel, MovieBasicInfo):
    __tablename__ = 'movie_basic_info'
    id: int = Field(primary_key=True)


movie_basic_info_dao = BaseDao(MovieBasicInfoModel)
movie_detail_dao = BaseDao(MovieDetailModel)
