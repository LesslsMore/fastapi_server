from typing import List

from model.collect.collect_source import FilmSource, SourceGrade, film_source_dao


class FilmSourceService:
    @staticmethod
    def find_collect_source_by_id(id: str) -> FilmSource:
        item = film_source_dao.query_item(filter_dict={"id": id})
        return item

    @staticmethod
    def get_collect_source_list_by_grade(grade: SourceGrade) -> List[FilmSource]:
        items = film_source_dao.query_items(filter_dict={"grade": grade})
        return items

    @staticmethod
    def add_collect_source(film_source: FilmSource) -> (bool, str):
        """
        添加采集站信息，若已存在则返回错误
        """
        film_source_dao.upsert(film_source)

        return True, "添加成功"

    @classmethod
    def exist_collect_source_list(cls) -> bool:
        """
        查询是否已经存在站点list相关数据
        """
        items = film_source_dao.query_all()
        return len(items) > 0

    @classmethod
    def update_collect_source(cls, film_source: FilmSource) -> bool:
        return cls.add_collect_source(film_source)
