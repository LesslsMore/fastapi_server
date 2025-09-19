from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import Column, JSON
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import SQLModel, Field

from dao.base_dao import BaseDao
from demo.sql import get_session


class KVModel(SQLModel, table=True):
    __tablename__ = 'key_value'
    id: int = Field(primary_key=True)
    key: Optional[str] = Field(default=None, description="key", unique=True)
    value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    expire_at: Optional[datetime] = Field(default=None, description="过期时间")


key_value_dao = BaseDao(KVModel)


class KVDao:
    @staticmethod
    def get_value(key: str):
        item = key_value_dao.query_item(filter_dict={'key': key})
        if item:
            # 检查是否过期
            if item.expire_at and item.expire_at < datetime.utcnow():
                # 如果过期，删除该记录并返回None
                key_value_dao.delete_item(filter_dict={'key': key})
                return None
            return item.value
        return None

    @staticmethod
    def set_value(key: str, value: dict, expire_in_seconds: Optional[int] = None) -> None:
        with get_session() as session:
            values = {
                'key': key,
                'value': value
            }

            # 如果设置了过期时间，则计算过期时间戳
            if expire_in_seconds is not None:
                expire_at = datetime.utcnow() + timedelta(seconds=expire_in_seconds)
                values['expire_at'] = expire_at

            stmt = insert(KVModel).values(**values)
            update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "key"}
            stmt = stmt.on_conflict_do_update(index_elements=['key'], set_=update_dict)
            session.exec(stmt)

    @staticmethod
    def exists(key: str) -> bool:
        item = key_value_dao.query_item(filter_dict={'key': key})
        if item:
            # 检查是否过期
            if item.expire_at and item.expire_at < datetime.utcnow():
                # 如果过期，删除该记录并返回False
                key_value_dao.delete_item(filter_dict={'key': key})
                return False
            return True
        return False

    @staticmethod
    def delete_key(key: str) -> bool:
        """
        删除指定的键
        """
        return key_value_dao.delete_item(filter_dict={'key': key})

    @staticmethod
    def ttl(key: str) -> Optional[int]:
        """
        获取键的剩余生存时间（秒）
        """
        item = key_value_dao.query_item(filter_dict={'key': key})
        if item and item.expire_at:
            if item.expire_at < datetime.utcnow():
                # 已过期，删除并返回None
                key_value_dao.delete_item(filter_dict={'key': key})
                return None
            return int((item.expire_at - datetime.utcnow()).total_seconds())
        elif item:
            # 没有设置过期时间，返回-1表示永不过期
            return -1
        else:
            # 键不存在
            return None
