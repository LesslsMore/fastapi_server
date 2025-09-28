from fastapi import APIRouter, Query

from model.system.manage import Banner, banner_dao
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/banner', tags=["海报"])


@router.get("/list", summary="轮播图列表")
def banner_list():
    items = banner_dao.query_all(['sort'])
    return ResponseUtil.success(data=items, msg="轮播图列表获取成功")


@router.get("/find", summary="Banner信息查询")
def banner_find(id: str = Query(...)):
    item = banner_dao.query_item({"id": id})
    return ResponseUtil.success(data=item, msg="Banner信息获取成功")


@router.post("/add", summary="Banner信息添加")
def banner_add(banner: Banner):
    item = banner_dao.upsert_item(banner)
    return ResponseUtil.success(data=item, msg="海报信息添加成功")


@router.post("/update", summary="Banner信息更新")
def banner_update(banner: Banner):
    item = banner_dao.upsert_item(banner)
    return ResponseUtil.success(data=item, msg="海报信息更新成功")


@router.get("/del", summary="Banner信息删除")
def banner_del(id: str = Query(...)):
    banner_dao.delete_item({"id": id})
    return ResponseUtil.success(msg="海报信息删除成功")
