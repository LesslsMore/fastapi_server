from fastapi import APIRouter, Query

from dao.system.failure_record import FailureRecordService
from model.collect.collect_source import film_source_dao
from model.system.virtual_object import RecordRequestVo
from plugin.spider.spider import SpiderService
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/record', tags=["记录"])


@router.get("/list", summary="获取采集失败记录列表")
def FailureRecordList(vo: RecordRequestVo = Query(...)):
    failure_record_list = FailureRecordService.failure_record_list()
    collect_source_list = film_source_dao.query_all()
    vo.paging = vo
    vo.beginTime = "0001-01-01T00:00:00Z"
    vo.endTime = "0001-01-01T00:00:00Z"
    data = {
        'params': vo,
        'list': [record.model_dump(by_alias=True) for record in failure_record_list],
        "options": {
            'origin': collect_source_list,
            'status': [
                {
                    "name": "全部",
                    "value": -1
                },
                {
                    "name": "待重试",
                    "value": 1
                },
                {
                    "name": "已处理",
                    "value": 0
                }
            ],
            'collectType': [
                {
                    "name": "全部",
                    "value": -1
                },
                {
                    "name": "影片详情",
                    "value": 0
                },
                {
                    "name": "文章",
                    "value": 1
                },
                {
                    "name": "演员",
                    "value": 2
                },
                {
                    "name": "角色",
                    "value": 3
                },
                {
                    "name": "网站",
                    "value": 4
                }
            ],
        },
    }
    return ResponseUtil.success(data=data, msg="影视源信息获取成功")


@router.get("/retry")
def CollectRecover(id: str = Query(..., description="资源站标识")):
    SpiderService.CollectRecover(id)
    return ResponseUtil.success(msg="采集重试已开启, 请勿重复操作")
