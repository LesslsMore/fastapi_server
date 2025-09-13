import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from dao.collect.categories import CategoryTreeService
from dao.collect.multiple_source import save_site_play_list
from dao.system.failure_record import FailureRecordService
from model.collect.collect_source import SourceGrade, ResourceType, FilmSource, film_source_dao
from model.system.failure_record import FailureRecord
from plugin.spider.spider_core import get_category_tree, get_page_count, get_film_detail


class SpiderService:
    @staticmethod
    def CollectRecover(id):
        fr = FailureRecordService.find_record_by_id(id)

        fs = film_source_dao.query_item(filter_dict={"id": fr.origin_id})

        SpiderService.collect_film(fs, fr.hour, fr.page_number)

    @staticmethod
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
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            FailureRecordService.save_failure_record(fr)
            logging.error(f"GetMovieDetail Error: {err}")
            return
        # 通过采集站 Grade 类型, 执行不同的存储逻辑
        if film_source.grade == SourceGrade.MasterCollect:
            pass
            # 主站点  保存完整影片详情信息到 redis

            # try:
            #     save_movie_detail_list(movie_detail_list)
            # except Exception as e:
            #     logging.info(f"SaveDetails Error: {e}")
            #     logging.error('save_details: %s', e)
        elif film_source.grade == SourceGrade.SlaveCollect:
            # 附属站点 仅保存影片播放信息到redis
            save_site_play_list(film_source.id, mac_vod_list)

    @staticmethod
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
            logging.info("Cannot Find Collect Source Site")
            return "Cannot Find Collect Source Site"
        elif not film_source.state:
            logging.info("The acquisition site was disabled")
            return "The acquisition site was disabled"
        # 主站点先采集分类树
        if film_source.grade == SourceGrade.MasterCollect and film_source.state:
            if not CategoryTreeService.exists_category_tree():
                SpiderService.collect_category(film_source)
        # h 参数校验
        if h == 0:
            logging.info("Collect time cannot be zero")
            return "Collect time cannot be zero"
        # 组装请求参数
        params = {}
        if h > 0:
            params['h'] = str(h)
        if 'jkun资源' in film_source.name:
            params.update({
                "t": 3,
                "wd": "mide",
            })
            # params.update({
            #     "wd": "高橋聖子",
            # })
        elif film_source.type_id and film_source.type_id > 0:
            params['t'] = str(film_source.type_id)
        # 2. 获取分页数，失败重试一次
        try:
            page_count = get_page_count(film_source.uri, params)
        except Exception as e:
            logging.error(f"GetPageCount Error: {e}")
            return str(e)
        # 3. 按采集类型分支
        if film_source.collectType == ResourceType.CollectVideo:
            # 采集视频资源
            if film_source.interval > 500:
                with ThreadPoolExecutor() as executor:
                    for i in range(1, page_count + 1):
                        executor.submit(SpiderService.collect_film, film_source, h, i, params)
                        time.sleep(film_source.interval / 1000)
            elif page_count <= 20:  # 假设 MAXGoroutine=10
                with ThreadPoolExecutor() as executor:
                    for i in range(1, page_count + 1):
                        executor.submit(SpiderService.collect_film, film_source, h, i, params)
            else:
                # 简化并发采集为串行（如需并发可用线程池）
                with ThreadPoolExecutor() as executor:
                    for i in range(1, page_count + 1):
                        executor.submit(SpiderService.collect_film, film_source, h, i, params)
        logging.info("Spider Task Exercise Success")

    @staticmethod
    def collect_film_by_id(ids: str, film_source: FilmSource):
        """
        采集指定ID的影片信息，兼容Go collectFilmById。
        """
        uri = film_source.uri
        params = {'pg': '1', 'ids': ids}
        mac_vod_list, err = get_film_detail(uri, params)
        if err:
            logging.info(f"get_film_detail Error: {err}")
            return
        if film_source.grade == SourceGrade.MasterCollect:
            pass
            # save_movie_detail(movie_detail_list[0])

            # if getattr(fs, 'syncPictures', False):
            #     try:
            #         save_virtual_pic(convert_virtual_picture(movie_list))
            #     except Exception as e:
            #         logging.info(f"SaveVirtualPic Error: {e}")
        elif film_source.grade == SourceGrade.SlaveCollect:
            save_site_play_list(film_source.id, mac_vod_list)

    @staticmethod
    def collect_category(s):
        """
        影视分类采集，对应 Go 端 CollectCategory。
        :param s: FilmSource对象，需包含uri等字段
        """
        try:
            category_tree = get_category_tree(s)
        except Exception as err:
            logging.info(f"GetCategoryTree Error: {err}")
            return
        CategoryTreeService.save_category_tree(category_tree)
