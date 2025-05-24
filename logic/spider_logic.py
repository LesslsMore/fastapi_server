import threading

from model.service.collect_source import FindCollectSourceById, get_collect_source_list_by_grade
from plugin.spider.spider import batch_collect, handle_collect, auto_collect, clear_spider, star_zero, collect_single_film, collect_category
from typing import List

class SpiderLogic:
    """
    Python 版 SpiderLogic，功能与 Go 端 SpiderLogic.go 保持一致。
    """
    def batch_collect(self, time: int, ids: List[str]):
        threading.Thread(target=batch_collect, args=(time, ids)).start()

    def start_collect(self, id: str, h: int):
        fs = FindCollectSourceById(id)
        if not fs:
            raise Exception("采集任务开启失败采集站信息不存在")
        def run():
            err = handle_collect(id, h)
            if err:
                print(f"资源站[{id}]采集任务执行失败: {err}")
        threading.Thread(target=run).start()

    def auto_collect(self, time: int):
        threading.Thread(target=auto_collect, args=(time,)).start()

    def clear_films(self):
        threading.Thread(target=clear_spider).start()

    def zero_collect(self, time: int):
        threading.Thread(target=star_zero, args=(time,)).start()

    def sync_collect(self, ids: str):
        threading.Thread(target=collect_single_film, args=(ids,)).start()

    def film_class_collect(self):
        l = get_collect_source_list_by_grade(MasterCollect)
        if not l:
            raise Exception("未获取到主采集站信息")
        for fs in l:
            if getattr(fs, 'state', True):
                threading.Thread(target=collect_category, args=(fs,)).start()
                return
        raise Exception("未获取到已启用的主采集站信息")