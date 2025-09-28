from pydantic import BaseModel
from sqlalchemy import Column, Integer
from sqlmodel import Field

from dao.base_dao import BaseDao
from demo.sql import BaseSQLModel


class BasicConfig(BaseModel):
    siteName: str
    domain: str
    logo: str
    keyword: str
    describe: str
    state: bool
    hint: str


class Banner(BaseSQLModel, table=True):
    __tablename__ = "banner"

    id: int = Field(sa_column=Column(Integer, primary_key=True))
    mid: int
    name: str
    year: int
    cName: str
    poster: str
    picture: str
    remark: str
    sort: int

banner_dao = BaseDao(Banner)
