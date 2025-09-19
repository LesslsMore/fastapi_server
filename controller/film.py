from fastapi import APIRouter, Query

from model.system.response import Page
from model.system.virtual_object import SearchVo
from service.film_logic import FilmLogic
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/film', tags=['影视'])


@router.get("/class/tree", summary="分类树")
async def FilmClassTree():
    tree = FilmLogic.GetFilmClassTree()
    return ResponseUtil.success(data=tree, msg="影片分类信息获取成功")


@router.get("/search/list", summary="影片分页")
async def FilmSearchPage(s: SearchVo = Query(...)):
    s.paging = Page(current=s.current, pageSize=s.pageSize)
    # 提供检索tag options
    options = FilmLogic.GetSearchOptions()
    # 检索条件
    sl = FilmLogic.GetFilmPage(s)
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


@router.get("/class/find")
async def FindFilmClass():
    return ResponseUtil.success(data=None, msg="查找成功")


@router.post("/class/update")
async def UpdateFilmClass():
    return ResponseUtil.success(data=None, msg="更新成功")


@router.get("/class/del")
async def DelFilmClass():
    return ResponseUtil.success(data=None, msg="删除成功")
