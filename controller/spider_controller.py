from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from logic.spider_logic import SpiderLogic
from model.service.collect_source import get_collect_source_list
from model.system.response import Page
from logic.index_logic import IndexLogic
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
    logic = SpiderLogic()
    if params.batch:
        if not params.ids or len(params.ids) == 0:
            return JSONResponse({"msg": "批量采集开启失败, 关联的资源站信息为空", "success": False}, status_code=400)
        logic.batch_collect(params.time, params.ids)
    else:
        if not params.id or len(params.id) == 0:
            return JSONResponse({"msg": "批量采集开启失败, 资源站Id获取失败", "success": False}, status_code=400)
        try:
            logic.start_collect(params.id, params.time)
        except Exception as e:
            return JSONResponse({"msg": f"采集任务开启失败: {str(e)}", "success": False}, status_code=400)
    # return JSONResponse({"msg": "采集任务已成功开启!!!", "success": True})
    return response.success(None, "采集任务已成功开启!!!")