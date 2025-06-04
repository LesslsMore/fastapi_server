from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
import json
from pydantic import BaseModel

from plugin.common.util.string_util import generate_salt


class SourceGrade(int, Enum):
    MasterCollect = 0
    SlaveCollect = 1


class CollectResultModel(int, Enum):
    JsonResult = 0
    XmlResult = 1


class ResourceType(int, Enum):
    CollectVideo = 0
    CollectArticle = 1
    CollectActor = 2
    CollectRole = 3
    CollectWebSite = 4

    def get_action_type(self) -> str:
        action_map = {
            ResourceType.CollectVideo: "detail",
            ResourceType.CollectArticle: "article",
            ResourceType.CollectActor: "actor",
            ResourceType.CollectRole: "role",
            ResourceType.CollectWebSite: "web",
        }
        return action_map.get(self, "detail")


class FilmSource(BaseModel):
    id: str = None
    name: str = None
    uri: str = None
    resultModel: CollectResultModel = None
    grade: SourceGrade = None
    syncPictures: bool = None
    collectType: ResourceType = None
    type_id: Optional[int] = -1  # 修改为Optional[int]以处理None值
    state: bool = None
    interval: Optional[int] = 0


class FilmSourceModel(SQLModel, FilmSource, table=True):
    __tablename__ = 'film_source'
    id: str = Field(default_factory=generate_salt, primary_key=True)
    uri: str = Field(default=None, unique=True)
