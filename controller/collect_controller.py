from fastapi import APIRouter, Query

from dao.system.failure_record import FailureRecordService
from model.system.virtual_object import RecordRequestVo
from plugin.spider.spider import SpiderService
from service.collect_logic import CollectLogic
from dao.collect.collect_source import FilmSourceService
from model.collect.collect_source import SourceGrade
from dao.collect.collect_source import FilmSource
from plugin.spider.spider_core import collect_api_test
from utils.response_util import ResponseUtil

collectController = APIRouter(prefix='/collect')


@collectController.get("/list")
def FilmSourceList():
    data = FilmSourceService.get_collect_source_list()
    return ResponseUtil.success(data=data, msg="影视源站点信息获取成功")


@collectController.get("/find")
def FindFilmSource(id: str = Query(..., description="资源站标识")):
    fs = FilmSourceService.find_collect_source_by_id(id)
    if fs is None:
        return ResponseUtil.error(msg="数据异常,资源站信息不存在")
    return ResponseUtil.success(data=fs, msg="原站点详情信息查找成功")


@collectController.post("/update")
def FilmSourceUpdate(s: FilmSource):
    # 参数校验
    if not s.id:
        return ResponseUtil.error(msg="参数异常, 资源站标识不能为空")
    # 业务逻辑处理
    result, msg = CollectLogic.update_film_source(s)
    if result:
        return ResponseUtil.success(msg="更新成功")
    else:
        return ResponseUtil.error(msg=msg)


@collectController.post("/change")
def FilmSourceChange(s: FilmSource):
    # 参数校验
    if not s.id:
        return ResponseUtil.error(msg="参数异常, 资源站标识不能为空")
    # 查找对应的资源站点信息
    fs = CollectLogic.get_film_source(s.id)
    if fs is None:
        return ResponseUtil.error(msg="数据异常,资源站信息不存在")
    # 如果采集站开启图片同步, 且采集站为附属站点则返回错误提示
    if s.syncPictures and fs.grade == SourceGrade.SlaveCollect:
        return ResponseUtil.error(msg="附属站点无法开启图片同步功能")
    # 检查状态和图片同步是否有变化
    if s.state != fs.state or s.syncPictures != fs.syncPictures:
        # 执行更新操作
        updated_source = FilmSource(**{
            "id": fs.id,
            "name": fs.name,
            "uri": fs.uri,
            "resultModel": fs.resultModel,
            "grade": fs.grade,
            "syncPictures": s.syncPictures,
            "collectType": fs.collectType,
            "state": s.state
        })
        # 更新资源站信息
        result, msg = CollectLogic.update_film_source(updated_source)
        if not result:
            return ResponseUtil.error(msg=f"资源站更新失败: {msg}")
    return ResponseUtil.success(msg="更新成功")


@collectController.post("/test")
def FilmSourceTest(s: dict):
    # 参数校验
    try:
        film_source = FilmSource(**s)
    except Exception as e:
        return ResponseUtil.error(msg=f"请求参数异常: {e}")
    # 业务校验（如有必要可补充）
    try:
        collect_api_test(film_source)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))
    return ResponseUtil.success(msg="测试成功!!!")


@collectController.get("/del")
def FilmSourceDel(id: str = Query(..., description="资源站标识")):
    # 参数校验
    if not id:
        return ResponseUtil.error(msg="参数异常, 资源站标识不能为空")
    # 删除采集站点
    if not CollectLogic.del_film_source(id):
        return ResponseUtil.error(msg="删除资源站失败")
    return ResponseUtil.success(msg="删除成功")


@collectController.post("/add")
def FilmSourceAdd(s: FilmSource):
    # 获取请求参数并校验
    if not s:
        return ResponseUtil.error(msg="请求参数异常")
    if not s.name or not s.uri:
        return ResponseUtil.error(msg="参数异常, 资源站标识、名称、地址不能为空")
    # 如果采集站开启图片同步, 且采集站为附属站点则返回错误提示
    if s.syncPictures and s.grade == SourceGrade.SlaveCollect:
        return ResponseUtil.error(msg="附属站点无法开启图片同步功能")
    # 执行 spider 测试
    try:
        collect_api_test(s)
    except Exception as e:
        return ResponseUtil.error(msg=f"资源接口测试失败, 请确认接口有效再添加: {e}")
    # 测试通过后将资源站信息添加到list
    result, msg = CollectLogic.save_film_source(s)
    if not result:
        return ResponseUtil.error(msg=f"资源站添加失败: {msg}")
    return ResponseUtil.success(msg="添加成功")


@collectController.get("/options")
def GetNormalFilmSource():
    data = FilmSourceService.get_collect_source_list()
    return ResponseUtil.success(data=data, msg="影视源信息获取成功")


@collectController.get("/record/list")
def FailureRecordList(vo: RecordRequestVo = Query(...)):
    failure_record_list = FailureRecordService.failure_record_list()
    collect_source_list = FilmSourceService.get_collect_source_list()
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


@collectController.get("/record/retry")
def CollectRecover(id: str = Query(..., description="资源站标识")):
    SpiderService.CollectRecover(id)
    return ResponseUtil.success(msg="采集重试已开启, 请勿重复操作")
