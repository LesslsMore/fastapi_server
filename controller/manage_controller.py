from fastapi import APIRouter, Depends, Query, HTTPException

from controller.collect_controller import collectController
from controller.spider_controller import spiderController
from controller.user_controller import userController
from logic.manage_logic import ManageLogic
from model.system.manage import BasicConfig, Banner
from model.system import response
from typing import List, Optional

router = APIRouter(prefix='/manage')
router.include_router(collectController)
router.include_router(spiderController)
router.include_router(userController)

def get_logic():
    return ManageLogic

# /manage/index
@router.get("/index")
def manage_index():
    # 这里可以根据实际业务返回管理后台首页数据
    return response.success({}, "管理后台首页数据获取成功")

# /manage/config/basic
@router.get("/config/basic")
def site_basic_config():
    data = ManageLogic.get_site_basic_config()
    return response.success(data, "基础配置信息获取成功")

# /manage/config/basic/update
@router.post("/manage/config/basic/update")
def update_site_basic(config: BasicConfig):
    if not config.domain or not config.site_name:
        return response.failed("域名和网站名称不能为空")
    try:
        ManageLogic.update_site_basic(config)
        return response.success_only_msg("更新成功")
    except Exception as e:
        return response.failed(f"网站配置更新失败: {e}")

# /manage/config/basic/reset
@router.get("/manage/config/basic/reset")
def reset_site_basic():
    try:
        ManageLogic.reset_site_basic()
        return response.success_only_msg("配置信息重置成功")
    except Exception as e:
        return response.failed(f"配置信息重置失败: {e}")

# /manage/banner/list
@router.get("/manage/banner/list")
def banner_list():
    banners = ManageLogic.get_banners()
    return response.success(banners, "轮播图列表获取成功")

# /manage/banner/find
@router.get("/manage/banner/find")
def banner_find(id: str = Query(...)):
    banners = ManageLogic.get_banners()
    for b in banners:
        if b.id == id:
            return response.success(b, "Banner信息获取成功")
    return response.failed("Banner信息获取失败")

# /manage/banner/add
@router.post("/manage/banner/add")
def banner_add(banner: Banner):
    banners = ManageLogic.get_banners()
    if len(banners) >= 6:
        return response.failed("Banners最大阈值为6, 无法添加新的banner信息")
    import uuid
    banner.id = str(uuid.uuid4())
    banners.append(banner)
    try:
        ManageLogic.save_banners(banners)
        return response.success_only_msg("海报信息添加成功")
    except Exception as e:
        return response.failed(f"Banners信息添加失败, {e}")

# /manage/banner/update
@router.post("/manage/banner/update")
def banner_update(banner: Banner):
    banners = ManageLogic.get_banners()
    for i, b in enumerate(banners):
        if b.id == banner.id:
            banners[i] = banner
            try:
                ManageLogic.save_banners(banners)
                return response.success_only_msg("海报信息更新成功")
            except Exception as e:
                return response.failed(f"海报信息更新失败: {e}")
    return response.failed("海报信息更新失败, 未匹配对应Banner信息")

# /manage/banner/del
@router.get("/manage/banner/del")
def banner_del(id: str = Query(...)):
    banners = ManageLogic.get_banners()
    for i, b in enumerate(banners):
        if b.id == id:
            banners.pop(i)
            ManageLogic.save_banners(banners)
            return response.success_only_msg("海报信息删除成功")
    return response.failed("海报信息删除失败")