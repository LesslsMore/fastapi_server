from typing import Optional

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
    # __table_args__ = (
    #     UniqueConstraint('key', name='uq_key')
    # )


key_value_dao = BaseDao(KVModel)


class KVDao:
    @staticmethod
    def get_value(key: str) -> str:
        item = key_value_dao.query_item(filter_dict={'key': key})
        return item.value

    @staticmethod
    def set_value(key: str, value: str) -> dict:
        with get_session() as session:
            values = {
                'key': key,
                'value': value
            }
            stmt = insert(KVModel).values(**values)
            update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "key"}
            stmt = stmt.on_conflict_do_update(index_elements=['key'], set_=update_dict)
            session.exec(stmt)

    @staticmethod
    def exists(key: str):
        item = key_value_dao.query_item(filter_dict={'key': key})
        return item.value
