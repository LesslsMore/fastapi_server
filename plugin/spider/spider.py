from dao.collect.multiple_source import save_site_play_list
from dao.collect.collect_source import FilmSourceService

from model.collect.collect_source import SourceGrade, ResourceType, FilmSource
from dao.collect.categories import CategoryTreeService

import time

from model.system.failure_record import FailureRecord
from datetime import datetime

from plugin.spider.spider_core import get_category_tree, get_page_count, get_film_detail
from dao.system.failure_record import save_failure_record
from dao.system.search import sync_search_info
import threading

from dao.system.search_tag import film_zero


def collect_film(film_source: FilmSource, h: int, pg: int, params: dict):
    """
    影视详情采集（单一源分页全采集），兼容Go collectFilm主流程。
    :param film_source: FilmSource对象，需包含uri、typeId、grade、syncPictures等字段
    :param h: 小时参数
    :param pg: 页码
    """
    uri = film_source.uri
    params.update({'pg': str(pg)})
    # if h > 0:
    #     params['h'] = str(h)
    # if film_source.type_id and film_source.type_id > 0:
    #     params['t'] = str(film_source.type_id)
    # 执行采集方法 获取影片详情list
    mac_vod_list, err = get_film_detail(uri, params)
    if err:
        fr = FailureRecord(
            origin_id=film_source.id,
            origin_name=film_source.name,
            uri=film_source.uri,
            collect_type=ResourceType.CollectVideo,
            page_number=pg,
            hour=h,
            cause=str(err),
            status=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        save_failure_record(fr)
        print(f"GetMovieDetail Error: {err}")
        return
    # 通过采集站 Grade 类型, 执行不同的存储逻辑
    if film_source.grade == SourceGrade.MasterCollect:
        pass
        # 主站点  保存完整影片详情信息到 redis

        # try:
        #     save_movie_detail_list(movie_detail_list)
        # except Exception as e:
        #     print(f"SaveDetails Error: {e}")
        #     logging.error('save_details: %s', e)
    elif film_source.grade == SourceGrade.SlaveCollect:
        # 附属站点 仅保存影片播放信息到redis
        save_site_play_list(film_source.id, mac_vod_list)


def handle_collect(h: int, film_source: FilmSource):
    ""
    """
    影视采集主流程，兼容Go HandleCollect。
    :param id: 采集站ID
    :param h: 时长参数
    """
    # 1. 获取采集站信息
    # film_source = FilmSourceService.find_collect_source_by_id(id)
    if not film_source:
        print("Cannot Find Collect Source Site")
        return "Cannot Find Collect Source Site"
    elif not film_source.state:
        print("The acquisition site was disabled")
        return "The acquisition site was disabled"
    # 主站点先采集分类树
    if film_source.grade == SourceGrade.MasterCollect and film_source.state:
        if not CategoryTreeService.exists_category_tree():
            collect_category(film_source)
    # h 参数校验
    if h == 0:
        print("Collect time cannot be zero")
        return "Collect time cannot be zero"
    # 组装请求参数
    params = {}
    if h > 0:
        params['h'] = str(h)
    if 'jkun资源' in film_source.name:
        # params.update({
        #     "t": 3,
        #     "wd": "mide",
        # })
        params.update({
            "wd": "高橋聖子",
        })
    elif film_source.type_id and film_source.type_id > 0:
        params['t'] = str(film_source.type_id)
    # 2. 获取分页数，失败重试一次
    try:
        page_count = get_page_count(film_source.uri, params)
    except Exception:
        try:
            page_count = get_page_count(film_source.uri, params)
        except Exception as e:
            print(f"GetPageCount Error: {e}")
            return str(e)
    # 3. 按采集类型分支
    if film_source.collectType == ResourceType.CollectVideo:
        # 采集视频资源
        if film_source.interval > 500:
            for i in range(1, page_count + 1):
                collect_film(film_source, h, i, params)
                time.sleep(film_source.interval / 1000)
        elif page_count <= 20:  # 假设 MAXGoroutine=10
            for i in range(1, page_count + 1):
                collect_film(film_source, h, i, params)
        else:
            # 简化并发采集为串行（如需并发可用线程池）
            for i in range(1, page_count + 1):
                collect_film(film_source, h, i, params)
        # 视频采集完成后同步信息
        if film_source.grade == SourceGrade.MasterCollect:
            if h > 0:
                sync_search_info(1)
            else:
                sync_search_info(0)
            # if getattr(s, 'syncPictures', False):
            #     # 假设有图片同步方法
            #     try:
            #         sync_film_picture()
            #     except Exception as e:
            #         print(f"SyncFilmPicture Error: {e}")
            # clear_cache()
    else:
        print("暂未开放此采集功能!!!")
        return "暂未开放此采集功能"
    print("Spider Task Exercise Success")
    return None


def collect_film_by_id(ids: str, film_source: FilmSource):
    """
    采集指定ID的影片信息，兼容Go collectFilmById。
    """
    uri = film_source.uri
    params = {'pg': '1', 'ids': ids}
    mac_vod_list, err = get_film_detail(uri, params)
    if err:
        print(f"get_film_detail Error: {err}")
        return
    if film_source.grade == SourceGrade.MasterCollect:
        pass
        # save_movie_detail(movie_detail_list[0])

        # if getattr(fs, 'syncPictures', False):
        #     try:
        #         save_virtual_pic(convert_virtual_picture(movie_list))
        #     except Exception as e:
        #         print(f"SaveVirtualPic Error: {e}")
    elif film_source.grade == SourceGrade.SlaveCollect:
        save_site_play_list(film_source.id, mac_vod_list)


def concurrent_page_spider(capacity: int, film_source, h: int, collect_func):
    """
    并发分页采集，简化为串行或可用线程池。
    """
    # 可用 concurrent.futures.ThreadPoolExecutor 实现真正并发
    for i in range(1, capacity + 1):
        collect_func(film_source, h, i)


def batch_collect(h: int, ids: list):
    """
    批量采集指定站点。
    """
    for id in ids:
        film_source = FilmSourceService.find_collect_source_by_id(id)
        if film_source and film_source.state:
            threading.Thread(target=handle_collect, args=(h, film_source)).start()


def auto_collect(h: int):
    """
    自动采集所有已启用站点。
    """
    for film_source in FilmSourceService.get_collect_source_list():
        if film_source.state:
            handle_collect(h, film_source)


def clear_spider():
    """
    删除所有已采集的影片信息。
    """

    film_zero()


def star_zero(h: int):
    """
    清空站点内所有影片信息并自动采集。
    """
    clear_spider()
    auto_collect(h)


def collect_single_film(ids: str):
    """
    通过影片唯一ID获取影片信息，仅处理主站点。
    """
    for film_source in FilmSourceService.get_collect_source_list():
        if film_source.grade == SourceGrade.MasterCollect and film_source.state:
            collect_film_by_id(ids, film_source)
            return


def collect_category(s):
    """
    影视分类采集，对应 Go 端 CollectCategory。
    :param s: FilmSource对象，需包含uri等字段
    """
    try:
        category_tree = get_category_tree(s)
    except Exception as err:
        print(f"GetCategoryTree Error: {err}")
        return
    CategoryTreeService.save_category_tree(category_tree)

