# 创建Session和Base
import contextlib
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String
from sqlmodel import Session, SQLModel, Field

from config.database import sync_engine


# Session = sessionmaker(bind=engine)
# Base = declarative_base(engine)


# 基础Mixin类
class BaseSQLModel(SQLModel):
    """model的基类,所有model都必须继承"""

    created_at: datetime = Field(sa_column=Column(DateTime, nullable=False, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        index=True
    ))
    deleted_at: datetime = Field(sa_column=Column(DateTime))  # 可以为空, 如果非空, 则为软删




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
