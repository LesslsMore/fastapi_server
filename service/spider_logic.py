from concurrent.futures import ThreadPoolExecutor
from typing import List

from model.collect.collect_source import film_source_dao
from plugin.spider.spider import SpiderService
from plugin.spider.spider_core import get_category_tree_by_db


class SpiderLogic:
    """
    Python 版 SpiderLogic，功能与 Go 端 SpiderLogic.go 保持一致。
    """

    @staticmethod
    def batch_collect(h: int, ids: List[str]):
        with ThreadPoolExecutor() as executor:
            for id in ids:
                film_source = film_source_dao.query_item(filter_dict={"id": id})
                if film_source and film_source.state:
                    executor.submit(SpiderService.handle_collect, h, film_source)

    @staticmethod
    def start_collect(id: str, h: int):
        with ThreadPoolExecutor() as executor:
            film_source = film_source_dao.query_item(filter_dict={"id": id})

            if film_source and film_source.state:
                executor.submit(SpiderService.handle_collect, h, film_source)

    @staticmethod
    def FilmClassCollect():
        get_category_tree_by_db()
