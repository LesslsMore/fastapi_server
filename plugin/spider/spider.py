from service.system.collect_source import FindCollectSourceById, get_collect_source_list, find_collect_source_by_id

from model.system.collect_source import SourceGrade, ResourceType, FilmSource
from service.system.categories import exists_category_tree, save_category_tree

import time
import logging

from model.system.failure_record import FailureRecord
from datetime import datetime

from plugin.spider.spider_core import get_category_tree, get_page_count, get_film_detail
from service.system.failure_record import save_failure_record
# from service.system.file_upload import save_virtual_pic
from service.system.movies import save_site_play_list, save_details, save_detail
from service.system.search import sync_search_info, film_zero


def collect_film(fs: FilmSource, h: int, pg: int):
    """
    影视详情采集（单一源分页全采集），兼容Go collectFilm主流程。
    :param fs: FilmSource对象，需包含uri、typeId、grade、syncPictures等字段
    :param h: 小时参数
    :param pg: 页码
    """
    uri = fs.uri
    params = {'pg': str(pg)}
    if h > 0:
        params['h'] = str(h)
    if fs.type_id and fs.type_id > 0:
        params['t'] = str(fs.type_id)
    # 执行采集方法 获取影片详情list
    movie_list, err = get_film_detail(uri, params)
    if err or not movie_list:
        fr = FailureRecord(
            origin_id=fs.id,
            origin_name=fs.name,
            uri=fs.uri,
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
    if fs.grade == SourceGrade.MasterCollect:
        # 主站点  保存完整影片详情信息到 redis

        try:
            save_details(movie_list)
        except Exception as e:
            print(f"SaveDetails Error: {e}")
            logging.error('save_details: %s', e)
        # if getattr(fs, 'syncPictures', False):
        #     try:
        #         from plugin.common.conver.Collect import convert_virtual_picture
        #         save_virtual_pic(convert_virtual_picture(movie_list))
        #     except Exception as e:
        #         print(f"SaveVirtualPic Error: {e}")
    elif fs.grade == SourceGrade.SlaveCollect:
        # 附属站点 仅保存影片播放信息到redis

        try:
            save_site_play_list(fs.id, movie_list)
        except Exception as e:
            print(f"save_site_play_list Error: {e}")


def handle_collect(id: str, h: int):
    """
    影视采集主流程，兼容Go HandleCollect。
    :param id: 采集站ID
    :param h: 时长参数
    """
    # 1. 获取采集站信息
    s = FindCollectSourceById(id)
    if not s:
        print("Cannot Find Collect Source Site")
        return "Cannot Find Collect Source Site"
    elif not getattr(s, 'state', True):
        print("The acquisition site was disabled")
        return "The acquisition site was disabled"
    # 主站点先采集分类树
    if getattr(s, 'grade', 0) == SourceGrade.MasterCollect and getattr(s, 'state', True):
        if not exists_category_tree():
            collect_category(s)
    # h 参数校验
    if h == 0:
        print("Collect time cannot be zero")
        return "Collect time cannot be zero"
    # 组装请求参数
    params = {}
    if h > 0:
        params['h'] = str(h)
    if s.type_id and s.type_id > 0:
        params['t'] = str(s.type_id)
    # 2. 获取分页数，失败重试一次
    try:
        page_count = get_page_count(s.uri, params)
    except Exception:
        try:
            page_count = get_page_count(s.uri, params)
        except Exception as e:
            print(f"GetPageCount Error: {e}")
            return str(e)
    # 3. 按采集类型分支
    if getattr(s, 'collectType', 1) == ResourceType.CollectVideo:
        # 采集视频资源
        if getattr(s, 'interval', 0) > 500:
            for i in range(1, page_count + 1):
                collect_film(s, h, i)
                time.sleep(s.interval / 1000)
        elif page_count <= 20:  # 假设 MAXGoroutine=10
            for i in range(1, page_count + 1):
                collect_film(s, h, i)
        else:
            # 简化并发采集为串行（如需并发可用线程池）
            for i in range(1, page_count + 1):
                collect_film(s, h, i)
        # 视频采集完成后同步信息
        if getattr(s, 'grade', 0) == SourceGrade.MasterCollect:
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


def collect_film_by_id(ids: str, fs: FilmSource):
    """
    采集指定ID的影片信息，兼容Go collectFilmById。
    """
    uri = fs.uri
    params = {'pg': '1', 'ids': ids}
    movie_list, err = get_film_detail(uri, params)
    if err or not movie_list:
        print(f"get_film_detail Error: {err}")
        return
    if fs.grade == SourceGrade.MasterCollect:
        save_detail(movie_list[0])

        # if getattr(fs, 'syncPictures', False):
        #     try:
        #         save_virtual_pic(convert_virtual_picture(movie_list))
        #     except Exception as e:
        #         print(f"SaveVirtualPic Error: {e}")
    elif fs.grade == SourceGrade.SlaveCollect:
        save_site_play_list(fs.id, movie_list)



def concurrent_page_spider(capacity: int, fs, h: int, collect_func):
    """
    并发分页采集，简化为串行或可用线程池。
    """
    # 可用 concurrent.futures.ThreadPoolExecutor 实现真正并发
    for i in range(1, capacity + 1):
        collect_func(fs, h, i)


def batch_collect(h: int, ids: list):
    """
    批量采集指定站点。
    """
    for id in ids:
        s = find_collect_source_by_id(id)
        if s and getattr(s, 'state', True):
            import threading
            threading.Thread(target=handle_collect, args=(s.id, h)).start()


def auto_collect(h: int):
    """
    自动采集所有已启用站点。
    """
    for s in get_collect_source_list():
        if getattr(s, 'state', True):
            handle_collect(s.id, h)


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
    for f in get_collect_source_list():
        if getattr(f, 'grade', 0) == SourceGrade.MasterCollect and getattr(f, 'state', True):
            collect_film_by_id(ids, f)
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
    try:
        save_category_tree(category_tree)
    except Exception as err:
        print(f"SaveCategoryTree Error: {err}")
