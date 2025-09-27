from fastapi import APIRouter

from config.data_config import INDEX_CACHE_KEY
from dao.collect.category import CategoryService
from dao.collect.kv_dao import KVDao
from dao.system.manage import ManageService
from service.index_logic import IndexLogic
from utils.response_util import ResponseUtil

router = APIRouter(tags=["主页"])


@router.get("/index", summary="主页")
def index_page():
    data = IndexLogic.index_page()
    return ResponseUtil.success(data=data, msg="首页数据获取成功")


@router.get("/config/basic", summary="基础配置")
def site_basic_config():
    data = ManageService.get_site_basic()
    return ResponseUtil.success(data=data, msg="基础配置信息获取成功")


@router.get("/navCategory", summary="导航分类")
def category_info():
    tree = CategoryService.get_category_tree_by_db()
    data = CategoryService.get_nav_category(tree)
    if not data:
        return ResponseUtil.error(msg="暂无分类信息")
    return ResponseUtil.success(data=data, msg="分类信息获取成功")


@router.get("/cache/del", summary="首页缓存删除")
def index_cache_del():
    KVDao.delete_key(INDEX_CACHE_KEY)
    return ResponseUtil.success(msg="首页缓存数据已清除!!!")
