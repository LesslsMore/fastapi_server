from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class FailureRecord(SQLModel, table=True):
    __tablename__ = "failure_records"
    id: Optional[int] = Field(default=None, primary_key=True)
    origin_id: str = Field(index=True, description="采集站唯一ID")
    origin_name: str = Field(description="采集站名称")
    uri: str = Field(description="采集源链接")
    collect_type: int = Field(description="采集类型")
    page_number: int = Field(default=1, description="页码")
    hour: int = Field(default=0, description="采集参数 h 时长")
    cause: str = Field(default="", description="失败原因")
    status: int = Field(default=1, description="重试状态")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")