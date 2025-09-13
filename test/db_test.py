from sqlalchemy import Column, Integer, String
from sqlmodel import SQLModel, Field

from config.database import sync_engine
from dao.base_dao import BaseDao
from demo.sql import get_session, BaseSQLModel


class User(BaseSQLModel, table=True):
    __tablename__ = "user"
    id: int = Field(sa_column=Column(Integer, primary_key=True))
    name: str = Field(sa_column=Column(String(36), nullable=True))
    phone: str = Field(sa_column=Column(String(36), nullable=True))


user_dao = BaseDao(User)

# 创建表
SQLModel.metadata.create_all(sync_engine)


def test():
    user_dao.update_item({'name': "张老三"}, update_dict={"phone": "123456"})


# 示例操作
def test_main():
    # 1. 插入数据
    with get_session() as session:
        user1 = User(name="张三", phone="13800138000")
        user2 = User(name="李四", phone="13900139000")
        session.add(user1)
        session.add(user2)
        # 提交在上下文管理器退出时自动完成

    # 2. 查询数据
    with get_session() as session:
        # 查询所有用户
        all_users = session.query(User).all()
        print("所有用户:", [f"{u.name}({u.phone})" for u in all_users])

        # 条件查询
        user = session.query(User).filter_by(name="张三").first()
        print("找到的用户:", user.name if user else "未找到")

        # 另一种条件查询方式
        user = session.query(User).filter(User.name == "李四").first()
        print("找到的用户:", user.name if user else "未找到")

    # 3. 更新数据
    with get_session() as session:
        user = session.query(User).filter_by(name="张三").first()
        if user:
            user.name = "张老三"
            # 提交在上下文管理器退出时自动完成

    # 4. 删除数据
    with get_session() as session:
        user = session.query(User).filter_by(name="李四").first()
        if user:
            session.delete(user)
            # 提交在上下文管理器退出时自动完成

    # 验证操作结果
    with get_session() as session:
        remaining_users = session.query(User).all()
        print("剩余用户:", [f"{u.name}({u.phone})" for u in remaining_users])
