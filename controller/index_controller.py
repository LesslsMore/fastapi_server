from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from model.system.response import Page
from logic.index_logic import IndexLogic
from model.system import response
from typing import Optional

router = APIRouter()

def get_logic():
    from plugin.db.mysql import db_engine
    from plugin.db.redis_client  import redis_client
    return IndexLogic(db_engine, redis_client)

@router.get("/index")
def index_page(logic: IndexLogic = Depends(get_logic)):
    data = logic.index_page()
    return response.success(data, "首页数据获取成功")

@router.get("/cache/del")
def index_cache_del(logic: IndexLogic = Depends(get_logic)):
    logic.clear_index_cache()
    return response.success_only_msg("首页缓存数据已清除!!!")

# @router.get("/config/basic")
# def site_basic_config(logic: IndexLogic = Depends(get_logic)):
#     data = logic.get_site_basic_config()
#     return response.success(data, "基础配置信息获取成功")

@router.get("/navCategory")
def categories_info(logic: IndexLogic = Depends(get_logic)):
    data = logic.get_nav_category()
    if not data:
        return response.failed("暂无分类信息")
    return response.success(data, "分类信息获取成功")

@router.get("/filmDetail")
def film_detail(id: int = Query(...), logic: IndexLogic = Depends(get_logic)):
    detail = logic.get_film_detail(id)
    page = Page(**{"pageSize": 14, "current": 0})
    relate = logic.relate_movie(detail, page)
    return response.success({"detail": detail, "relate": relate}, "影片详情信息获取成功")

@router.get("/filmPlayInfo")
def film_play_info(
    id: int = Query(...),
    playFrom: Optional[str] = Query(""),
    episode: int = Query(0),
    logic: IndexLogic = Depends(get_logic)
):
    detail = logic.get_film_detail(id)
    if len(playFrom) <= 1 and len(detail["list"]) > 0:
        playFrom = detail["list"][0]["id"]
    current_play = None
    for v in detail.get("list", []):
        if v["id"] == playFrom:
            current_play = v["linkList"][episode] if episode < len(v["linkList"]) else None
            break
    page = Page(**{"pageSize": 14, "current": 0})
    relate = logic.relate_movie(detail, page)
    return response.success({
        "detail": detail,
        "current": current_play,
        "currentPlayFrom": playFrom,
        "currentEpisode": episode,
        "relate": relate
    }, "影片播放信息获取成功")

@router.get("/searchFilm")
def search_film(
    keyword: str = Query(""),
    current: int = Query(1),
    logic: IndexLogic = Depends(get_logic)
):
    pageSize = 10
    page = Page(**{"pageSize": 10, "current": current})
    bl = logic.search_film_info(keyword.strip(), page)
    page = {"pageSize": pageSize, "current": current, "total": len(bl)}
    if page["total"] <= 0:
        return response.failed("暂无相关影片信息")
    return response.success({"list": bl, "page": page}, "影片搜索成功")

@router.get("/filmClassify")
def film_classify(
    Pid: int = Query(...),
    logic: IndexLogic = Depends(get_logic)
):
    title = logic.get_pid_category(Pid)
    page = {"pageSize": 21, "current": 1}
    content = logic.get_film_classify(Pid, 1, 21)
    return response.success({"title": title, "content": content}, "分类影片信息获取成功")

@router.get("/filmClassifySearch")
def film_tag_search(
    Pid: int = Query(...),
    Category: Optional[int] = Query(None),
    Plot: Optional[str] = Query(""),
    Area: Optional[str] = Query(""),
    Language: Optional[str] = Query(""),
    Year: Optional[int] = Query(None),
    Sort: str = Query("update_stamp"),
    current: int = Query(1),
    logic: IndexLogic = Depends(get_logic)
):
    params = {
        "Pid": str(Pid),
        "Cid": str(Category) if Category else "",
        "Plot": Plot,
        "Area": Area,
        "Language": Language,
        "Year": str(Year) if Year else "",
        "Sort": Sort
    }
    pageSize = 49
    page = {"pageSize": pageSize, "current": current}
    film_list = logic.get_films_by_tags(params, current, pageSize)
    title = logic.get_pid_category(Pid) if logic.get_pid_category(Pid) else ""
    search = logic.search_tags(Pid)
    params['Category'] = params.pop('Cid')
    return response.success({
        "title": title,
        "list": film_list,
        "search": search,
        "params": params,
        "page": page
    }, "分类影片数据获取成功")