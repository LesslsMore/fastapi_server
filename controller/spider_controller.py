from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from service.spider_logic import SpiderLogic
from model.system import response
from typing import Optional, List

spiderController = APIRouter(prefix='/spider')


class CollectParams(BaseModel):
    time: int
    batch: bool = False
    ids: Optional[List[str]] = None
    id: Optional[str] = None


@spiderController.post("/start")
def star_spider(params: CollectParams):
    if params.time == 0:
        return JSONResponse({"msg": "采集开启失败,采集时长不能为0", "success": False}, status_code=400)
    if params.batch:
        if not params.ids or len(params.ids) == 0:
            return JSONResponse({"msg": "批量采集开启失败, 关联的资源站信息为空", "success": False}, status_code=400)
        SpiderLogic.batch_collect(params.time, params.ids)
    else:
        if not params.id or len(params.id) == 0:
            return JSONResponse({"msg": "批量采集开启失败, 资源站Id获取失败", "success": False}, status_code=400)
        try:
            SpiderLogic.start_collect(params.id, params.time)
        except Exception as e:
            return JSONResponse({"msg": f"采集任务开启失败: {str(e)}", "success": False}, status_code=400)
    # return JSONResponse({"msg": "采集任务已成功开启!!!", "success": True})
    return response.success(None, "采集任务已成功开启!!!")


@spiderController.get("/class/cover")
def CoverFilmClass():
    SpiderLogic.FilmClassCollect()
    return response.success(None, "影视分类信息重置成功, 请稍等片刻后刷新页面")
