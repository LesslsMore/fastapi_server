from fastapi import APIRouter

from model.system.manage import BasicConfig
from service.manage_logic import ManageLogic
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/config', tags=["配置"])


@router.get("/basic")
def site_basic_config():
    data = ManageLogic.get_site_basic_config()
    return ResponseUtil.success(data=data, msg="基础配置信息获取成功")


# /manage/config/basic/update
@router.post("/basic/update")
def update_site_basic(config: BasicConfig):
    if not config.domain or not config.site_name:
        return ResponseUtil.error(msg="域名和网站名称不能为空")
    try:
        ManageLogic.update_site_basic(config)
        return ResponseUtil.success(msg="更新成功")
    except Exception as e:
        return ResponseUtil.error(msg=f"网站配置更新失败: {e}")


# /manage/config/basic/reset
@router.get("/basic/reset")
def reset_site_basic():
    try:
        ManageLogic.reset_site_basic()
        return ResponseUtil.success(msg="配置信息重置成功")
    except Exception as e:
        return ResponseUtil.error(msg=f"配置信息重置失败: {e}")
