import contextlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Session, SQLModel, Field

from config.database import sync_engine


# 定义 UTC+8 时区
def get_time(hours: int = 8):
    return datetime.now(timezone(timedelta(hours=hours)))


# 基础Mixin类
# class BaseSQLModel(SQLModel):
#     """model的基类,所有model都必须继承"""
#
#     created_at: datetime = Field(sa_column=Column(DateTime, nullable=False, default=get_time))
#     updated_at: datetime = Field(sa_column=Column(
#         DateTime,
#         nullable=False,
#         default=get_time,
#         onupdate=get_time,
#         index=True
#     ))
#     deleted_at: datetime = Field(sa_column=Column(DateTime))  # 可以为空, 如果非空, 则为软删


# 基础Mixin类
class BaseSQLModel(SQLModel):
    """model的基类,所有model都必须继承"""

    # 使用 Field 定义字段，而不是直接使用 Column
    created_at: datetime = Field(
        default_factory=get_time,
        sa_column_kwargs={"nullable": False}
    )
    updated_at: datetime = Field(
        default_factory=get_time,
        sa_column_kwargs={
            "nullable": False,
            "onupdate": get_time
        }
    )
    deleted_at: Optional[datetime] = Field(default=None)

# 会话上下文管理器
@contextlib.contextmanager
def get_session():
    session = Session(sync_engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# 定义User模型
# class User(BaseModel, table=True):
#     __tablename__ = "user"
#     id: int = Field(sa_column=Column(Integer, primary_key=True))
#     name: str = Field(sa_column=Column(String(36), nullable=True))
#     phone: str = Field(sa_column=Column(String(36), nullable=True))
