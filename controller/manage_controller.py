from fastapi import APIRouter, Depends, Query

from controller.index_controller import indexController
from model.system.manage import BasicConfig, Banner
from plugin.middleware.handle_jwt import AuthToken
from service.index_logic import IndexLogic
from service.manage_logic import ManageLogic
from utils.response_util import ResponseUtil

manageController = APIRouter(prefix='/manage', tags=["管理"], dependencies=[Depends(AuthToken)])


# /manage/index
@manageController.get("/index")
def manage_index():
    # 这里可以根据实际业务返回管理后台首页数据
    data = {}
    return ResponseUtil.success(data=data, msg="管理后台首页数据获取成功")


# /manage/config/basic
@manageController.get("/config/basic")
def site_basic_config():
    data = ManageLogic.get_site_basic_config()
    return ResponseUtil.success(data=data, msg="基础配置信息获取成功")


# /manage/config/basic/update
@manageController.post("/manage/config/basic/update")
def update_site_basic(config: BasicConfig):
    if not config.domain or not config.site_name:
        return ResponseUtil.error(msg="域名和网站名称不能为空")
    try:
        ManageLogic.update_site_basic(config)
        return ResponseUtil.success(msg="更新成功")
    except Exception as e:
        return ResponseUtil.error(msg=f"网站配置更新失败: {e}")


# /manage/config/basic/reset
@manageController.get("/manage/config/basic/reset")
def reset_site_basic():
    try:
        ManageLogic.reset_site_basic()
        return ResponseUtil.success(msg="配置信息重置成功")
    except Exception as e:
        return ResponseUtil.error(msg=f"配置信息重置失败: {e}")


# /manage/banner/list
@manageController.get("/banner/list", summary="轮播图列表")
def banner_list():
    banners = ManageLogic.get_banners()
    return ResponseUtil.success(data=banners, msg="轮播图列表获取成功")


@indexController.get("/cache/del", summary="首页缓存删除")
def index_cache_del():
    IndexLogic.clear_index_cache()
    return ResponseUtil.success(msg="首页数据获取成功")


# /manage/banner/find
@manageController.get("/manage/banner/find")
def banner_find(id: str = Query(...)):
    banners = ManageLogic.get_banners()
    for b in banners:
        if b.id == id:
            return ResponseUtil.success(data=b, msg="Banner信息获取成功")
    return ResponseUtil.error(msg="Banner信息获取失败")


# /manage/banner/add
@manageController.post("/manage/banner/add")
def banner_add(banner: Banner):
    banners = ManageLogic.get_banners()
    if len(banners) >= 6:
        return ResponseUtil.error(msg="Banners最大阈值为6, 无法添加新的banner信息")
    import uuid
    banner.id = str(uuid.uuid4())
    banners.append(banner)
    try:
        ManageLogic.save_banners(banners)
        return ResponseUtil.success(msg="海报信息添加成功")
    except Exception as e:
        return ResponseUtil.error(msg=f"Banners信息添加失败, {e}")


# /manage/banner/update
@manageController.post("/manage/banner/update")
def banner_update(banner: Banner):
    banners = ManageLogic.get_banners()
    for i, b in enumerate(banners):
        if b.id == banner.id:
            banners[i] = banner
            try:
                ManageLogic.save_banners(banners)
                return ResponseUtil.success(msg="海报信息更新成功")
            except Exception as e:
                return ResponseUtil.error(msg=f"海报信息更新失败: {e}")
    return ResponseUtil.error(msg="海报信息更新失败, 未匹配对应Banner信息")


# /manage/banner/del
@manageController.get("/manage/banner/del")
def banner_del(id: str = Query(...)):
    banners = ManageLogic.get_banners()
    for i, b in enumerate(banners):
        if b.id == id:
            banners.pop(i)
            ManageLogic.save_banners(banners)
            return ResponseUtil.success(msg="海报信息删除成功")
    return ResponseUtil.error(msg="海报信息删除失败")
