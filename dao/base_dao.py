from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Field
from sqlmodel import Session

from config.constant import IOrderEnum
from config.database import sync_engine
from demo.sql import get_session
from utils.page_util import PageUtil
from typing import List, Optional, Tuple
from sqlalchemy import select, func, asc, desc, and_
# from sqlalchemy.orm import Session
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
import contextlib

class ConfigPageQueryModel(SQLModel):
    """
    参数配置管理分页查询模型
    """

    page_num: Optional[int] = Field(default=1, description='当前页码')
    page_size: Optional[int] = Field(default=10, description='每页记录数')


# 1. 统一模型定义和操作映射
OP_MAPPING = {
    "==": lambda f, v: f == v,
    ">": lambda f, v: f > v,
    "<": lambda f, v: f < v,
    ">=": lambda f, v: f >= v,
    "<=": lambda f, v: f <= v,
    "!=": lambda f, v: f != v,
    "like": lambda f, v: f.ilike(f"%{v}%") if not v.startswith(('%', '_')) else f.ilike(v),
    "in": lambda f, v: f.in_(v),
    "not_in": lambda f, v: ~f.in_(v),
    "is_null": lambda f, _: f.is_(None),
    "not_null": lambda f, _: f.is_not(None)
}

# 2. 简化模型定义
class PageModel(BaseModel):
    page_no: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    result: List = None
    total: int = None
    header: List = None

class SortModel(BaseModel):
    field: str
    order: str = "asc"  # 默认值

class FilterModel(BaseModel):
    field_name: str
    field_ops: str
    field_value: Optional[object] = None

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

    # def paginate(self):
    #     with Session(self.engine) as session:
    #         return paginate(session, select(self.model).order_by(self.model.created_at))

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

    def get_items(self, page: PageModel = None,
                  sorts: List[SortModel] = None,
                  filters: List[FilterModel] = None,
                  distinct_fields: List[str] = None) -> Tuple[List, int]:
        """
        获取分页数据及总数

        :return: (数据列表, 总数)
        """
        # 基础查询
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        # 应用过滤条件
        if filters:
            conditions = self._build_conditions(filters)
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # 应用排序
        if sorts:
            query = self._apply_sort(query, sorts)

        # 应用去重
        if distinct_fields:
            distinct_cols = [getattr(self.model, field) for field in distinct_fields]
            query = query.distinct(*distinct_cols)
            # 计数查询也需要去重
            count_query = select(func.count()).select_from(query.subquery())

        # 应用分页
        if page:
            query = query.offset((page.page_no - 1) * page.page_size).limit(page.page_size)
        paginated_data = []
        # 执行查询
        with Session(self.engine) as session:
            items = session.exec(query).all()
            total = session.scalar(count_query) if not distinct_fields else session.scalar(count_query)
            for row in items:
                if row and len(row) == 1:
                    paginated_data.append(row[0])
                else:
                    paginated_data.append(row)

        return paginated_data, total

    def _build_conditions(self, filters: List[FilterModel]) -> List:
        """构建过滤条件"""
        conditions = []
        for filt in filters:
            if not hasattr(self.model, filt.field_name):
                raise ValueError(f"无效字段: {filt.field_name}")

            field = getattr(self.model, filt.field_name)
            op_func = OP_MAPPING.get(filt.field_ops)

            if not op_func:
                raise ValueError(f"无效操作符: {filt.field_ops}")

            # 处理特殊操作符
            if filt.field_ops in ["in", "not_in"] and not isinstance(filt.field_value, list):
                filt.field_value = [filt.field_value]

            conditions.append(op_func(field, filt.field_value))

        return conditions

    def _apply_sort(self, query, sorts: List[SortModel]):
        """应用排序"""
        order_clauses = []
        for sort in sorts:
            if not hasattr(self.model, sort.field):
                raise ValueError(f"无效排序字段: {sort.field}")

            field = getattr(self.model, sort.field)
            order_clauses.append(desc(field) if sort.order == "desc" else asc(field))

        return query.order_by(*order_clauses)
