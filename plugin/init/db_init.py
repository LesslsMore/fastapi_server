# // TableInIt 初始化 mysql 数据库相关数据
from sqlmodel import SQLModel

from config.database import sync_engine
# from plugin.db import get_session
from dao.system.user_dao import init_admin_account


def table_init():
    # session = get_session()
    SQLModel.metadata.create_all(sync_engine)

    init_admin_account()