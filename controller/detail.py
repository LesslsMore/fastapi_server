from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel
from starlette.requests import Request

from dao.collect.category import CategoryService
from dao.system.search_mac_vod import get_mac_vod_list_by_sort, get_relate_mac_vod_basic_info, get_search_tag_by_stat
from model.collect.category import Category
from model.system.movies import MovieDetail
from model.system.response import Page
from service.index_logic import IndexLogic
from utils.response_util import ResponseUtil

router = APIRouter(tags=["详情"])


@router.get("/filmClassify", summary="分类数据")
def film_classify(request: Request, category: Category = Query(...)):
    pid = category.pid if isinstance(category.pid, int) else category.Pid
    title = CategoryService.get_pid_category(pid)
    content = {
        "news": get_mac_vod_list_by_sort(['vod_year', 'vod_time'], pid),
        "top": get_mac_vod_list_by_sort(['vod_hits'], pid),
        "recent": get_mac_vod_list_by_sort(['vod_time'], pid)
    }

    data = {"title": title, "content": content}
    return ResponseUtil.success(data=data, msg="分类影片信息获取成功")


class FilmClassifySearchRequest(BaseModel):
    Pid: int
    Category: Optional[int] = None
    Plot: Optional[str] = ""
    Area: Optional[str] = ""
    Language: Optional[str] = ""
    Year: Optional[int] = None
    Sort: str = "update_stamp"
    current: int = 1


@router.get("/filmClassifySearch", summary="分类搜索数据")
def film_tag_search(
        request: FilmClassifySearchRequest = Query(...)
):
    params = {
        "Pid": str(request.Pid),
        "Cid": str(request.Category) if request.Category else "",
        "Plot": request.Plot,
        "Area": request.Area,
        "Language": request.Language,
        "Year": str(request.Year) if request.Year else "",
        "Sort": request.Sort
    }
    # pageSize = 49
    # page = {"pageSize": pageSize, "current": current}
    page = Page(pageSize=49, current=request.current)
    # film_list = IndexLogic.get_films_by_tags(params, page)
    film_list = IndexLogic.get_mac_vod_list_by_tags(params, page)
    title = CategoryService.get_pid_category(request.Pid) if CategoryService.get_pid_category(request.Pid) else ""

    pid = request.Pid
    search = get_search_tag_by_stat(pid)

    params['Category'] = params.pop('Cid')
    data = {
        "title": title,
        "list": film_list,
        "search": search,
        "params": params,
        "page": page.model_dump(),
    }
    return ResponseUtil.success(data=data, msg="分类影片数据获取成功")


@router.get("/searchFilm", summary="搜索数据")
def search_film(
        keyword: str = Query(""),
        current: int = Query(1),
):
    pageSize = 10
    page = Page(**{"pageSize": 10, "current": current})
    # bl = IndexLogic.search_film_info(keyword.strip(), page)

    bl = IndexLogic.search_mac_vod_info(keyword.strip(), page)

    page = {"pageSize": pageSize, "current": current, "total": len(bl)}
    if page["total"] <= 0:
        return ResponseUtil.error(msg="暂无相关影片信息")
    data = {"list": bl, "page": page}
    return ResponseUtil.success(data=data, msg="影片搜索成功")


@router.get("/filmDetail", summary="详情数据")
def film_detail(id: int = Query(...)):
    detail = IndexLogic.get_film_detail(id)

    page = Page(**{"pageSize": 14, "current": 0})
    movie_detail = MovieDetail(**detail)
    relate = get_relate_mac_vod_basic_info(movie_detail, page)

    data = {"detail": detail, "relate": relate}
    return ResponseUtil.success(data=data, msg="影片详情信息获取成功")


@router.get("/filmPlayInfo", summary="播放数据")
def film_play_info(
        id: int = Query(...),
        playFrom: Optional[str] = Query(""),
        episode: int = Query(0),
):
    detail = IndexLogic.get_film_detail(id)
    if len(playFrom) <= 1 and len(detail["list"]) > 0:
        playFrom = detail["list"][0]["id"]
    current_play = None
    for v in detail.get("list", []):
        if v["id"] == playFrom:
            current_play = v["linkList"][episode] if episode < len(v["linkList"]) else None
            break

    page = Page(**{"pageSize": 14, "current": 0})
    movie_detail = MovieDetail(**detail)
    relate = get_relate_mac_vod_basic_info(movie_detail, page)

    data = {
        "detail": detail,
        "current": current_play,
        "currentPlayFrom": playFrom,
        "currentEpisode": episode,
        "relate": relate
    }
    return ResponseUtil.success(data=data, msg="影片播放信息获取成功")
