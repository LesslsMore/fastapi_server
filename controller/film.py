from fastapi import APIRouter, Query

from dao.system.search import GetSearchPage
from model.system.response import Page
from model.system.virtual_object import SearchVo
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/film', tags=['影视'])


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
