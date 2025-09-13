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
            update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "id"}
            stmt = stmt.on_conflict_do_update(index_elements=[self.model.id], set_=update_dict)
            session.exec(stmt)
            session.commit()

    def upsert_items(self, items: list):
        with get_session() as session:
            table = self.model.__table__
            data = [d.dict() if hasattr(d, 'dict') else d.__dict__ for d in items]
            stmt = insert(table).values(data)
            update_dict = {c.name: getattr(stmt.excluded, c.name) for c in table.columns if c.name != 'id'}
            stmt = stmt.on_conflict_do_update(index_elements=['id'], set_=update_dict)
            session.execute(stmt)
            session.commit()

        # with get_session() as session:
        #     values = film_source.model_dump()
        #     stmt = insert(FilmSourceModel).values(**values)
        #     update_dict = {c: stmt.excluded[c] for c in values.keys() if c != "id"}
        #     stmt = stmt.on_conflict_do_update(index_elements=[FilmSourceModel.id], set_=update_dict)
        #     session.exec(stmt)
        #     session.commit()

    def delete_item(self, filter_dict: dict):
        with get_session() as session:
            item = session.query(self.model).filter_by(**filter_dict).first()
            if item:
                session.delete(item)

    def create_item(self, item):
        with get_session() as session:
            session.add(item)

        # """
        # 通过Id删除对应的采集站点信息
        # """
        # with get_session() as session:
        #     stat = delete(FilmSourceModel).where(FilmSourceModel.id == id)
        #     session.exec(stat)
        #     session.commit()
        #     return True
        # return False

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

    # with get_session() as session:
    #     statement = select(FilmSourceModel).where(FilmSourceModel.grade == grade)
    #     results = session.exec(statement).all()
    #     return results

    # with get_session() as session:
    #     statement = select(FilmSourceModel).where(FilmSourceModel.id == id)
    #     results = session.exec(statement).one_or_none()
    #     return results

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
        # .where(MacVod.type_id_1 == pid).order_by(MacVod.vod_time.desc())

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

        # with get_session() as session:
        #     # 计算总数
        #     count = session.exec(select(func.count()).select_from(SearchInfo).where(SearchInfo.cid == cid)).one()
        #     page.total = count
        #     page.pageCount = (page.total + page.pageSize - 1) // page.pageSize
        #
        #     # 查询数据
        #     query = select(SearchInfo).where(SearchInfo.cid == cid).order_by(SearchInfo.update_stamp.desc()) \
        #         .offset((page.current - 1) * page.pageSize).limit(page.pageSize)
        #     search_info_list = session.exec(query).all()
