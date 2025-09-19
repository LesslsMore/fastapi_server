from fastapi import APIRouter

from service.index_logic import IndexLogic
from service.manage_logic import ManageLogic
from utils.response_util import ResponseUtil

router = APIRouter(tags=["主页"])


@router.get("/index", summary="主页")
def index_page():
    data = IndexLogic.index_page()
    return ResponseUtil.success(data=data, msg="首页数据获取成功")


@router.get("/config/basic", summary="基础配置")
def site_basic_config():
    data = ManageLogic.get_site_basic_config()
    return ResponseUtil.success(data=data, msg="基础配置信息获取成功")


@router.get("/navCategory", summary="导航分类")
def categories_info():
    data = IndexLogic.get_nav_category()
    if not data:
        return ResponseUtil.error(msg="暂无分类信息")
    return ResponseUtil.success(data=data, msg="分类信息获取成功")

# @indexController.get("/cache/del")
# def index_cache_del():
#     IndexLogic.clear_index_cache()
#     return ResponseUtil.success(msg="首页数据获取成功")
