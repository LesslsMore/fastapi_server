from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from logic.collect_logic import CollectLogic
from model.service.collect_source import get_collect_source_list
from model.system.collect_source import FilmSource, SourceGrade
from model.service.collect_source import FilmSource
from model.service.collect_source import FindCollectSourceById
from model.system import response
from plugin.spider.spider_core import collect_api_test

collectController = APIRouter(prefix='/collect')


@collectController.get("/list")
def FilmSourceList():
    data = get_collect_source_list()
    return response.success(data, "影视源站点信息获取成功")


@collectController.get("/find")
def FindFilmSource(id: str = Query(..., description="资源站标识")):

    fs = FindCollectSourceById(id)
    if fs is None:
        return response.failed("数据异常,资源站信息不存在")
    return response.success(fs, "原站点详情信息查找成功")


@collectController.post("/update")
def FilmSourceUpdate(s: FilmSource):

    # 参数校验
    if not s.id:
        return response.failed("参数异常, 资源站标识不能为空")
    # 业务逻辑处理
    result, msg = CollectLogic.update_film_source(s)
    if result:
        return response.success_only_msg("更新成功")
    else:
        return response.failed(msg)


@collectController.post("/change")
def FilmSourceChange(s: FilmSource):


    # 参数校验
    if not s.id:
        return response.failed("参数异常, 资源站标识不能为空")
    # 查找对应的资源站点信息
    fs = CollectLogic.get_film_source(s.id)
    if fs is None:
        return response.failed("数据异常,资源站信息不存在")
    # 如果采集站开启图片同步, 且采集站为附属站点则返回错误提示
    if s.syncPictures and fs.grade == SourceGrade.SlaveCollect:
        return response.failed("附属站点无法开启图片同步功能")
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
            return response.failed(f"资源站更新失败: {msg}")
    return response.success_only_msg("更新成功")


@collectController.post("/test")
def FilmSourceTest(s: dict):

    # 参数校验
    try:
        film_source = FilmSource(**s)
    except Exception as e:
        return response.failed(f"请求参数异常: {e}")
    # 业务校验（如有必要可补充）
    try:
        collect_api_test(film_source)
    except Exception as e:
        return response.failed(str(e))
    return response.success_only_msg("测试成功!!!")


@collectController.get("/del")
def FilmSourceDel(id: str = Query(..., description="资源站标识")):

    # 参数校验
    if not id:
        return response.failed("参数异常, 资源站标识不能为空")
    # 删除采集站点
    if not CollectLogic.del_film_source(id):
        return response.failed("删除资源站失败")
    return response.success_only_msg("删除成功")


