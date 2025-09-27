from fastapi import APIRouter, Query

from dao.collect.category import CategoryService
from model.collect.MacType import mac_type_dao, MacTypeDto
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/class', tags=['分类'])


@router.get("/tree", summary="分类树")
async def FilmClassTree():
    tree = CategoryService.get_category_tree()
    return ResponseUtil.success(data=tree, msg="影片分类信息获取成功")


@router.get("/find", summary="分类信息")
async def FindFilmClass(dto: MacTypeDto = Query(...)):
    # item = mac_type_dao.query_item(filter_dict={"type_id": dto.id})

    tree = CategoryService.get_category_tree()
    item = tree.find_by_id(dto.id)
    return ResponseUtil.success(data=item, msg="查找成功")


@router.post("/update", summary="更新分类信息")
async def UpdateFilmClass(dto: MacTypeDto):
    mac_type_dao.update_item(filter_dict={"type_id": dto.id}, update_dict={"type_status": 1 if dto.show else 0})
    return ResponseUtil.success(data=None, msg="更新成功")


@router.get("/del", summary="删除分类信息")
async def DelFilmClass(dto: MacTypeDto = Query(...)):
    mac_type_dao.delete_item(filter_dict={"type_id": dto.id})
    return ResponseUtil.success(data=None, msg="删除成功")
