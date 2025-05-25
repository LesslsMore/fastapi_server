# // TableInIt 初始化 mysql 数据库相关数据
from service.collect.film_detail import create_film_detail_table
from service.system.user_service import init_admin_account


def table_init():
    # create_user_table()



    # create_search_table()
    #
    # create_failure_record_table()

    create_film_detail_table()

    init_admin_account()