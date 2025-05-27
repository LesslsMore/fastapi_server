# // TableInIt 初始化 mysql 数据库相关数据
from sqlmodel import SQLModel

from plugin.db import get_session
from service.system.user_service import init_admin_account


def table_init():
    session = get_session()
    SQLModel.metadata.create_all(session.get_bind())

    init_admin_account()