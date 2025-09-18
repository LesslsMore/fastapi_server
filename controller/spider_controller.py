import logging

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from service.spider_logic import SpiderLogic
from utils.response_util import ResponseUtil
from typing import Optional, List

spiderController = APIRouter(prefix='/spider', tags=['爬虫'])


class CollectParams(BaseModel):
    time: int
    batch: bool = False
    ids: Optional[List[str]] = None
    id: Optional[str] = None


@spiderController.post("/start")
def star_spider(params: CollectParams):
    logging.info(f"开始采集任务, 采集时长: {params.time}, 资源站Id: {params.id}, 资源站Ids: {params.ids}, 批量采集: {params.batch}")
    if params.time == 0:
        return ResponseUtil.error(msg="采集开启失败,采集时长不能为0")
    if params.batch:
        if not params.ids or len(params.ids) == 0:
            return ResponseUtil.error(msg="批量采集开启失败, 关联的资源站信息为空")
        SpiderLogic.batch_collect(params.time, params.ids)
    else:
        if not params.id or len(params.id) == 0:
            return ResponseUtil.error(msg="批量采集开启失败, 资源站Id获取失败")
        try:
            SpiderLogic.start_collect(params.id, params.time)
        except Exception as e:
            return ResponseUtil.error(msg=f"采集任务开启失败: {str(e)}")
    return ResponseUtil.success(msg="采集任务已成功开启!!!")


@spiderController.get("/class/cover")
def CoverFilmClass():
    SpiderLogic.FilmClassCollect()
    return ResponseUtil.success(msg="影视分类信息重置成功, 请稍等片刻后刷新页面")