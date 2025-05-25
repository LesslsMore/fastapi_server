import threading

from service.collect.collect_source import find_collect_source_by_id, get_collect_source_list_by_grade
from model.collect.collect_source import SourceGrade
from plugin.spider.spider import batch_collect, handle_collect, auto_collect, clear_spider, star_zero, \
    collect_single_film, collect_category
from typing import List


class SpiderLogic:
    """
    Python 版 SpiderLogic，功能与 Go 端 SpiderLogic.go 保持一致。
    """

    @staticmethod
    def batch_collect(time: int, ids: List[str]):
        threading.Thread(target=batch_collect, args=(time, ids)).start()

    @staticmethod
    def start_collect(id: str, h: int):
        fs = find_collect_source_by_id(id)
        if not fs:
            raise Exception("采集任务开启失败采集站信息不存在")

        def run():
            err = handle_collect(id, h)
            if err:
                print(f"资源站[{id}]采集任务执行失败: {err}")

        threading.Thread(target=run).start()

    @staticmethod
    def auto_collect(time: int):
        threading.Thread(target=auto_collect, args=(time,)).start()

    @staticmethod
    def clear_films():
        threading.Thread(target=clear_spider).start()

    @staticmethod
    def zero_collect(time: int):
        threading.Thread(target=star_zero, args=(time,)).start()

    @staticmethod
    def sync_collect(ids: str):
        threading.Thread(target=collect_single_film, args=(ids,)).start()

    @staticmethod
    def film_class_collect():
        l = get_collect_source_list_by_grade(SourceGrade.MasterCollect)
        if not l:
            raise Exception("未获取到主采集站信息")
        for fs in l:
            if getattr(fs, 'state', True):
                threading.Thread(target=collect_category, args=(fs,)).start()
                return
        raise Exception("未获取到已启用的主采集站信息")
