from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, JSON
from sqlmodel import Field

from dao.base_dao import BaseDao
from demo.sql import BaseSQLModel


class AnimeVod(BaseSQLModel, table=True):
    __tablename__ = "anime_vod"
    vod_id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True}, description="影片ID")
    vod_name: str = Field(description="影片名称")
    vod_play_url: Optional[dict] = Field(default={}, sa_column=Column(JSON), description="播放地址")
    vod_pic: str = Field(description="图片地址")
    bangumi: Optional[dict] = Field(default={}, sa_column=Column(JSON), description="番剧信息")
    # created_at: datetime = Field(default_factory=lambda: datetime.now())
    # updated_at: datetime = Field(default_factory=lambda: datetime.now())


# 添加新的 Pydantic 模型用于 upsert 和 search 接口
class AnimeVodUpsertRequest(BaseModel):
    vod_id: int
    name: str
    episode: int
    url: str
    vod_pic: str
    bangumi: Optional[dict] = {}


class AnimeVodSearchRequest(BaseModel):
    name: str
    episode: Optional[int] = None


anime_vod_dao = BaseDao(AnimeVod)
