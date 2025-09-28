import logging
from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import ValidationInfo

from model.collect.collect_source import film_source_dao, SourceGrade
from service.spider.spider import SpiderService
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/spider', tags=['爬虫'])


class CollectParams(BaseModel):
    time: int
    batch: bool = False
    ids: Optional[List[str]] = None
    id: Optional[str] = None

    @field_validator('time')
    @classmethod
    def validate_time(cls, v, info: ValidationInfo):
        # 在 Pydantic V2 中，需要通过 info.data 获取其他字段的值
        if v == 0:
            raise ValueError('time 不能为零')
        return v

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v, info: ValidationInfo):
        # 在 Pydantic V2 中，需要通过 info.data 获取其他字段的值
        if info.data.get('batch') and (not v or len(v) == 0):
            raise ValueError('批量采集时，资源站Ids不能为空')
        return v

    @field_validator('id')
    @classmethod
    def validate_id(cls, v, info: ValidationInfo):
        # 在 Pydantic V2 中，需要通过 info.data 获取其他字段的值
        if not info.data.get('batch') and (not v or len(v) == 0):
            raise ValueError('单次采集时，资源站Id不能为空')
        return v


@router.post("/start")
async def star_spider(params: CollectParams):
    logging.info(
        f"开始采集任务, 采集时长: {params.time}, 资源站Id: {params.id}, 资源站Ids: {params.ids}, 批量采集: {params.batch}")

    if params.batch:
        SpiderService.batch_collect(params.time, params.ids)
    else:
        SpiderService.batch_collect(params.time, [params.id])
    return ResponseUtil.success(msg="采集任务已成功开启!!!")


@router.get("/class/cover", summary="影视分类信息重置")
def CoverFilmClass():
    film_source_list = film_source_dao.query_items({
        'grade': SourceGrade.MasterCollect,
        'state': True,
    })
    for film_source in film_source_list:
        SpiderService.collect_category(film_source)

    return ResponseUtil.success(msg="影视分类信息重置成功, 请稍等片刻后刷新页面")
