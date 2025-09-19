from fastapi import APIRouter, Query

from model.system.manage import Banner
from service.manage_logic import ManageLogic
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/banner', tags=["海报"])


@router.get("/list", summary="轮播图列表")
def banner_list():
    banners = ManageLogic.get_banners()
    return ResponseUtil.success(data=banners, msg="轮播图列表获取成功")


# /manage/banner/find
@router.get("/find")
def banner_find(id: str = Query(...)):
    banners = ManageLogic.get_banners()
    for b in banners:
        if b.id == id:
            return ResponseUtil.success(data=b, msg="Banner信息获取成功")
    return ResponseUtil.error(msg="Banner信息获取失败")


# /manage/banner/add
@router.post("/add")
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
@router.post("/update")
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
@router.get("/del")
def banner_del(id: str = Query(...)):
    banners = ManageLogic.get_banners()
    for i, b in enumerate(banners):
        if b.id == id:
            banners.pop(i)
            ManageLogic.save_banners(banners)
            return ResponseUtil.success(msg="海报信息删除成功")
    return ResponseUtil.error(msg="海报信息删除失败")
