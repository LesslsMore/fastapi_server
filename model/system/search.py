from __future__ import annotations

from typing import List, Optional, Any
from pydantic import BaseModel, field_serializer, ConfigDict
from pydantic.alias_generators import to_pascal, to_camel
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


# SearchInfo 数据模型
class SearchInfo(SQLModel):
    __tablename__ = 'search'
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        alias="ID"  # JSON 键名强制大写
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        alias="CreatedAt",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        alias="UpdatedAt",
        sa_column_kwargs={"name": "updated_at"}
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        alias="DeletedAt"
    )
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

    # @field_serializer("created_at", "updated_at", "deleted_at")
    # def serialize_datetime(self, dt: datetime) -> str:
    #     return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

    @field_serializer("created_at", "updated_at", "deleted_at")
    def serialize_datetime(self, dt: datetime) -> Optional[str]:
        if dt is None:  # 处理 deleted_at 可能为 None
            return None
        # 转换为带时区的格式（如 +08:00）
        return dt.astimezone().isoformat(timespec='microseconds')

    # 4. 启用全局驼峰转换配置
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True  # 允许通过别名初始化模型
    )


class Tag(BaseModel):
    name: str
    value: Any
