from fastapi import APIRouter, Query

from dao.system.failure_record import FailureRecordService
from model.collect.collect_source import SourceGrade, film_source_dao, FilmSource
from model.system.virtual_object import RecordRequestVo
from plugin.spider.spider import SpiderService
from plugin.spider.spider_core import collect_api_test
from service.collect_logic import CollectLogic
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/collect', tags=["采集"])


@router.get("/list")
def FilmSourceList():
    items = film_source_dao.query_all()
    return ResponseUtil.success(data=items, msg="影视源站点信息获取成功")


@router.get("/find")
def FindFilmSource(id: str = Query(..., description="资源站标识")):
    item = film_source_dao.query_item(filter_dict={"id": id})
    if item is None:
        return ResponseUtil.error(msg="数据异常,资源站信息不存在")
    return ResponseUtil.success(data=item, msg="原站点详情信息查找成功")


@router.post("/update")
def FilmSourceUpdate(film_source: FilmSource):
    # 参数校验
    if not film_source.id:
        return ResponseUtil.error(msg="参数异常, 资源站标识不能为空")

    film_source_dao.upsert(film_source)
    return ResponseUtil.success(msg="更新成功")


@router.post("/change")
def FilmSourceChange(s: FilmSource):
    # 参数校验
    if not s.id:
        return ResponseUtil.error(msg="参数异常, 资源站标识不能为空")
    # 查找对应的资源站点信息

    fs = film_source_dao.query_item(filter_dict={"id": s.id})
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

        film_source_dao.upsert(updated_source)

    return ResponseUtil.success(msg="更新成功")


@router.post("/test")
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


@router.get("/del")
def FilmSourceDel(id: str = Query(..., description="资源站标识")):
    # 参数校验
    if not id:
        return ResponseUtil.error(msg="参数异常, 资源站标识不能为空")
    # 删除采集站点
    if not CollectLogic.del_film_source(id):
        return ResponseUtil.error(msg="删除资源站失败")
    return ResponseUtil.success(msg="删除成功")


@router.post("/add")
def FilmSourceAdd(film_source: FilmSource):
    # 获取请求参数并校验

    if not film_source:
        return ResponseUtil.error(msg="请求参数异常")
    if not film_source.name or not film_source.uri:
        return ResponseUtil.error(msg="参数异常, 资源站标识、名称、地址不能为空")
    # 如果采集站开启图片同步, 且采集站为附属站点则返回错误提示
    if film_source.syncPictures and film_source.grade == SourceGrade.SlaveCollect:
        return ResponseUtil.error(msg="附属站点无法开启图片同步功能")
    # 执行 spider 测试
    try:
        collect_api_test(film_source)
    except Exception as e:
        return ResponseUtil.error(msg=f"资源接口测试失败, 请确认接口有效再添加: {e}")
    # 测试通过后将资源站信息添加到list
    film_source_dao.upsert(film_source)

    return ResponseUtil.success(msg="添加成功")


@router.get("/options")
def GetNormalFilmSource():
    items = film_source_dao.query_all()
    return ResponseUtil.success(data=items, msg="影视源信息获取成功")


