from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
import json
from pydantic import BaseModel

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
    result_model: CollectResultModel = None
    grade: SourceGrade = None
    sync_pictures: bool = None
    collect_type: ResourceType = None
    state: bool = None
    interval: int = None