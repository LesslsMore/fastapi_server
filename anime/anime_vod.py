from datetime import datetime
from typing import Optional, List, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class AnimeVod(SQLModel, table=True):
    __tablename__ = "anime_vod"
    vod_id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True}, description="影片ID")
    vod_name: str = Field(description="影片名称")
    vod_play_url: Optional[dict] = Field(default={}, sa_column=Column(JSON), description="播放地址")
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
