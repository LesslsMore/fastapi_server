from sqlalchemy.dialects.postgresql import insert
from sqlmodel import SQLModel
from sqlmodel import Session

from plugin.db import pg_engine


class BaseDao:
    def __init__(self, model: SQLModel):
        self.model = model

    # 提取的公共方法
    def upsert(self, item: SQLModel):
        with Session(pg_engine) as session:
            values = item.model_dump()
            stmt = insert(self.model).values(**values)
            update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "id"}
            stmt = stmt.on_conflict_do_update(index_elements=[self.model.id], set_=update_dict)
            session.exec(stmt)
            session.commit()
