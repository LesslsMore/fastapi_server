from typing import Optional

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Field
from sqlmodel import Session

from config.constant import IOrderEnum
from config.database import sync_engine
from demo.sql import get_session
from utils.page_util import PageUtil


class ConfigPageQueryModel(SQLModel):
    """
    参数配置管理分页查询模型
    """

    page_num: Optional[int] = Field(default=1, description='当前页码')
    page_size: Optional[int] = Field(default=10, description='每页记录数')


class BaseDao:
    def __init__(self, model: SQLModel, engine: Engine = sync_engine):
        self.model = model
        self.engine = engine

    # 提取的公共方法
    def upsert(self, item: SQLModel):
        with get_session() as session:
            values = item.model_dump()
            stmt = insert(self.model).values(**values)

            pks = [pk.name for pk in self.model.__table__.primary_key]

            update_dict = {c: stmt.excluded[c] for c in values.keys() if c not in pks}
            stmt = stmt.on_conflict_do_update(index_elements=pks, set_=update_dict)
            session.exec(stmt)
            session.commit()

    def upsert_items(self, items: list):
        with get_session() as session:
            table = self.model.__table__
            data = [d.dict() if hasattr(d, 'dict') else d.__dict__ for d in items]
            stmt = insert(table).values(data)

            pks = [pk.name for pk in self.model.__table__.primary_key]

            update_dict = {c.name: getattr(stmt.excluded, c.name) for c in table.columns if c.name not in pks}
            stmt = stmt.on_conflict_do_update(index_elements=pks, set_=update_dict)
            session.execute(stmt)
            session.commit()

    def delete_item(self, filter_dict: dict):
        with get_session() as session:
            item = session.query(self.model).filter_by(**filter_dict).first()
            if item:
                session.delete(item)

    def create_item(self, item):
        with get_session() as session:
            session.add(item)

    def update_item(self, filter_dict: dict, update_dict: dict):
        with get_session() as session:
            session.query(self.model).filter_by(**filter_dict).update(update_dict)

    def query_item(self, filter_dict: dict):
        with Session(self.engine) as session:
            item = session.query(self.model).filter_by(**filter_dict).first()
            return item

    def query_items(self, filter_dict: dict):
        with Session(self.engine) as session:
            items = session.query(self.model).filter_by(**filter_dict).all()
            return items

    def query_items_by_ids(self, ids: list):
        with Session(self.engine) as session:
            # 构建批量查询语句
            statement = select(self.model).where(
                self.model.vod_id.in_(ids)  # 使用 IN 操作符匹配多个 ID
            )
            results = session.exec(statement)
            return results.all()  # 返回所有匹配结果的列表

    def query_all(self):
        with Session(self.engine) as session:
            items = session.query(self.model).order_by(self.model.name.desc()).all()
            return items

    def paginate(self):
        with Session(self.engine) as session:
            return paginate(session, select(self.model).order_by(self.model.created_at))

    def page_items(self, filter_dict: dict = {},
                   order_bys: list[str] = ["id"],
                   order: IOrderEnum = IOrderEnum.descendent,
                   query_object: ConfigPageQueryModel = ConfigPageQueryModel(),
                   is_page: bool = True):
        """
        根据查询参数获取参数配置列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 参数配置列表信息对象
        """

        with Session(self.engine) as session:

            columns = self.model.__table__.columns

            if order == IOrderEnum.ascendent:
                order_bys = [columns[order_by].asc() for order_by in order_bys]
            else:
                order_bys = [columns[order_by].desc() for order_by in order_bys]

            query = select(self.model).filter_by(**filter_dict).order_by(*order_bys)

            config_list = PageUtil.paginate(session, query, query_object.page_num, query_object.page_size,
                                            is_page)

            return config_list
