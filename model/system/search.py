from typing import List, Optional, Any
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from datetime import datetime


# SearchInfo 数据模型
class SearchInfo(SQLModel, table=True):
    __tablename__ = 'search'
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = Field(default=None)
    mid: int
    cid: int
    pid: int
    name: str
    sub_title: Optional[str] = None
    c_name: Optional[str] = None
    class_tag: Optional[str] = None
    area: Optional[str] = None
    language: Optional[str] = None
    year: Optional[int] = None
    initial: Optional[str] = None
    score: Optional[float] = None
    update_stamp: Optional[int] = None
    hits: Optional[int] = None
    state: Optional[str] = None
    remarks: Optional[str] = None
    release_stamp: Optional[int] = None


class Tag(BaseModel):
    name: str
    value: Any
