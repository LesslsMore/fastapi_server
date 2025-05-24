# // TableInIt 初始化 mysql 数据库相关数据
from model.service.failure_record import create_failure_record_table
from model.service.film_detail import create_film_detail_table
from model.service.user_service import create_user_table, init_admin_account


def table_init():
    # create_user_table()



    # create_search_table()
    #
    # create_failure_record_table()

    create_film_detail_table()

    init_admin_account()