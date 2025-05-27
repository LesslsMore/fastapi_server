from typing import List

from service.collect.collect_source import save_collect_source_list, exist_collect_source_list
from model.collect.collect_source import FilmSource, SourceGrade, CollectResultModel, ResourceType
from plugin.common.util.string_util import generate_salt


# FilmSourceInit 初始化预存站点信息，提供一些预存采集连Api链接
def film_source_init():
    # 首先获取filmSourceList数据, 如果存在则直接返回
    if exist_collect_source_list():
        return
    l: List[FilmSource] = [
        FilmSource(id=generate_salt(), type_id=-1, name="天涯资源", uri="https://tyyszy.com/api.php/provide/vod",
                   resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False,
                   collectType=ResourceType.CollectVideo, state=False),
        FilmSource(id=generate_salt(), type_id=-1, name="如意资源", uri="https://cj.rycjapi.com/api.php/provide/vod",
                   resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False,
                   collectType=ResourceType.CollectVideo, state=False),
        FilmSource(id=generate_salt(), type_id=30, name="HD(LZ)", uri="https://cj.lziapi.com/api.php/provide/vod/", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.MasterCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=True),
        FilmSource(id=generate_salt(), type_id=-1, name="HD(BF)", uri="https://bfzyapi.com/api.php/provide/vod/", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=False, interval=2500),
        FilmSource(id=generate_salt(), type_id=-1, name="HD(FF)", uri="http://cj.ffzyapi.com/api.php/provide/vod/", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=False),
        FilmSource(id=generate_salt(), type_id=-1, name="HD(OK)", uri="https://okzyapi.com/api.php/provide/vod/", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=False),
        FilmSource(id=generate_salt(), type_id=-1, name="HD(HM)", uri="https://json.heimuer.xyz/api.php/provide/vod/", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=False),
        FilmSource(id=generate_salt(), type_id=-1, name="HD(LY)", uri="https://360zy.com/api.php/provide/vod/at/json", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=False),
        FilmSource(id=generate_salt(), type_id=-1, name="HD(SN)", uri="https://suoniapi.com/api.php/provide/vod/from/snm3u8/", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=False, interval=2000),
        FilmSource(id=generate_salt(), type_id=-1, name="HD(DB)", uri="https://caiji.dbzy.tv/api.php/provide/vod/from/dbm3u8/at/josn/", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=False),
        FilmSource(id=generate_salt(), type_id=-1, name="HD(IK)", uri="https://ikunzyapi.com/api.php/provide/vod/at/json", resultModel=CollectResultModel.JsonResult, grade=SourceGrade.SlaveCollect, syncPictures=False, collectType=ResourceType.CollectVideo, state=False),
    ]
    err = save_collect_source_list(l)
    if err:
        print(f"SaveSourceApiList Error: {err}")