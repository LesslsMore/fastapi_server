from dao.base_dao import db_view_init
from dao.system.manage import ManageService
from model.collect.collect_source import film_source_dao
from model.system.manage import BasicConfig, banner_dao


# FilmSourceInit 初始化预存站点信息，提供一些预存采集连Api链接
def film_source_init():
    # 首先获取filmSourceList数据, 如果存在则直接返回
    items = film_source_dao.query_all(['name'])
    if len(items) > 0:
        return
    db_view_init('sql/init.sql')


def basic_config_init():
    # Initialize website basic configuration
    basic_config = BasicConfig(
        siteName="资源帝",
        domain="http://127.0.0.1:3600",
        logo="https://s2.loli.net/2023/12/05/O2SEiUcMx5aWlv4.jpg",
        keyword="在线视频, 免费观影",
        describe="你想要的我都有!",
        state=True,
        hint="网站升级中, 暂时无法访问 !!!"
    )
    ManageService.save_site_basic(basic_config)


def banner_init():
    # 首先获取filmSourceList数据, 如果存在则直接返回
    items = banner_dao.query_all(['sort'])
    if len(items) > 0:
        return
    db_view_init('sql/init_banner.sql')
