from fastapi import APIRouter, Query

from dao.collect.category import CategoryService
from dao.system.search import GetSearchPage
from model.collect.MacType import mac_type_dao, MacTypeDto
from model.system.response import Page
from model.system.virtual_object import SearchVo
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/film', tags=['影视'])


@router.get("/class/tree", summary="分类树")
async def FilmClassTree():
    tree = CategoryService.get_category_tree()
    return ResponseUtil.success(data=tree, msg="影片分类信息获取成功")


@router.get("/class/find", summary="分类信息")
async def FindFilmClass(dto: MacTypeDto = Query(...)):
    # item = mac_type_dao.query_item(filter_dict={"type_id": dto.id})

    tree = CategoryService.get_category_tree()
    item = tree.find_by_id(dto.id)
    return ResponseUtil.success(data=item, msg="查找成功")


@router.post("/class/update", summary="更新分类信息")
async def UpdateFilmClass(dto: MacTypeDto):
    mac_type_dao.update_item(filter_dict={"type_id": dto.id}, update_dict={"type_status": 1 if dto.show else 0})
    return ResponseUtil.success(data=None, msg="更新成功")


@router.get("/class/del", summary="删除分类信息")
async def DelFilmClass(dto: MacTypeDto = Query(...)):
    mac_type_dao.delete_item(filter_dict={"type_id": dto.id})
    return ResponseUtil.success(data=None, msg="删除成功")


@router.get("/search/list", summary="影片分页")
async def FilmSearchPage(s: SearchVo = Query(...)):
    s.paging = Page(current=s.current, pageSize=s.pageSize)
    # 提供检索tag options
    options = None
    # 检索条件
    sl = GetSearchPage(s)
    data = {
        "params": s.model_dump(),
        "list": [s.model_dump(by_alias=True) for s in sl],
        "options": options,
    }
    return ResponseUtil.success(data=data, msg="影片分页信息获取成功")


@router.post("/add")
async def FilmAdd():
    return ResponseUtil.success(data=None, msg="添加成功")


@router.get("/search/del")
async def FilmDelete():
    return ResponseUtil.success(data=None, msg="删除成功")
