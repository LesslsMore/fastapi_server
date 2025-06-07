from fastapi import APIRouter, Depends, HTTPException, Request, Query

from logic.film_logic import FilmLogic
from logic.user_logic import UserLogic
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from model.system import response
from model.system.response import Page
from model.system.virtual_object import SearchVo

filmController = APIRouter(prefix='/film')


@filmController.post("/add")
async def FilmAdd():
    return response.success()


@filmController.get("/search/list")
async def FilmSearchPage(s: SearchVo = Query(...)):
    s.paging = Page(current=s.current, pageSize=s.pageSize)
    # s = SearchVo(paging=Page())
    # 提供检索tag options
    options = FilmLogic.GetSearchOptions()
    # 检索条件
    sl = FilmLogic.GetFilmPage(s)
    return response.success({
        "params": s.model_dump(),
        "list": [s.model_dump(by_alias=True) for s in sl],
        "options": options,
    }, "影片分页信息获取成功")


@filmController.get("/search/del")
async def FilmDelete():
    return response.success()


@filmController.get("/class/tree")
async def FilmClassTree():
    tree = FilmLogic.GetFilmClassTree()
    return response.success(tree, "影片分类信息获取成功")


@filmController.get("/class/find")
async def FindFilmClass():
    return response.success()


@filmController.post("/class/update")
async def UpdateFilmClass():
    return response.success()


@filmController.get("/class/del")
async def DelFilmClass():
    return response.success()
