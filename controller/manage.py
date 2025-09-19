from fastapi import APIRouter, Depends

from plugin.middleware.handle_jwt import AuthToken
from service.index_logic import IndexLogic
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/manage', tags=["管理"], dependencies=[Depends(AuthToken)])


@router.get("/index")
def manage_index():
    # 这里可以根据实际业务返回管理后台首页数据
    data = {}
    return ResponseUtil.success(data=data, msg="管理后台首页数据获取成功")


@router.get("/cache/del", summary="首页缓存删除")
def index_cache_del():
    IndexLogic.clear_index_cache()
    return ResponseUtil.success(msg="首页数据获取成功")
