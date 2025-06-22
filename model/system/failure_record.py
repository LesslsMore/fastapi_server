from typing import Optional

from pydantic import field_serializer, ConfigDict
from pydantic.alias_generators import to_camel, to_pascal
from sqlmodel import SQLModel, Field
from datetime import datetime


class FailureRecord(SQLModel, table=True):
    __tablename__ = "failure_records"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        alias="ID"  # JSON 键名强制大写
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        alias="CreatedAt",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        alias="UpdatedAt",
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        alias="DeletedAt"
    )

    origin_id: str = Field(index=True, description="采集站唯一ID", alias="originId")
    origin_name: str = Field(description="采集站名称", alias="originName")
    uri: str = Field(description="采集源链接", alias="uri")
    collect_type: int = Field(description="采集类型", alias="collectType")
    page_number: int = Field(default=1, description="页码", alias="pageNumber")
    hour: int = Field(default=0, description="采集参数 h 时长", alias="hour")
    cause: str = Field(default="", description="失败原因", alias="cause")
    status: int = Field(default=1, description="重试状态", alias="status")

    @field_serializer("created_at", "updated_at", "deleted_at")
    def serialize_datetime(self, dt: datetime) -> Optional[str]:
        if dt is None:  # 处理 deleted_at 可能为 None
            return None
        # 转换为带时区的格式（如 +08:00）
        return dt.astimezone().isoformat(timespec='microseconds')
        # 转换为你想要的格式： "2025-06-22 17:49:54"
        # return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    # 4. 启用全局驼峰转换配置
    model_config = ConfigDict(
        # alias_generator=to_pascal,
        alias_generator=to_camel,
        populate_by_name=True  # 允许通过别名初始化模型
    )
