from fastapi import APIRouter, Depends, HTTPException, Request, Query

from service.film_logic import FilmLogic
from service.user_logic import UserLogic
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from model.system import response
from model.system.response import Page
from model.system.virtual_object import SearchVo
from utils.response_util import ResponseUtil

filmController = APIRouter(prefix='/film')


@filmController.post("/add")
async def FilmAdd():
    return ResponseUtil.success(data=None, msg="添加成功")


@filmController.get("/search/list")
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


@filmController.get("/search/del")
async def FilmDelete():
    return ResponseUtil.success(data=None, msg="删除成功")


@filmController.get("/class/tree")
async def FilmClassTree():
    tree = FilmLogic.GetFilmClassTree()
    return ResponseUtil.success(data=tree, msg="影片分类信息获取成功")


@filmController.get("/class/find")
async def FindFilmClass():
    return ResponseUtil.success(data=None, msg="查找成功")


@filmController.post("/class/update")
async def UpdateFilmClass():
    return ResponseUtil.success(data=None, msg="更新成功")


@filmController.get("/class/del")
async def DelFilmClass():
    return ResponseUtil.success(data=None, msg="删除成功")
