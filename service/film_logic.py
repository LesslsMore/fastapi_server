from typing import List

from model.system.search import SearchInfo
from model.system.virtual_object import SearchVo
from dao.collect.categories import CategoryTreeService
from dao.system.search import GetSearchPage


class FilmLogic:
    @staticmethod
    def GetFilmClassTree():
        return CategoryTreeService.get_category_tree()

    @staticmethod
    def GetFilmPage(s: SearchVo) -> List[SearchInfo]:
        # 获取影片检索信息分页数据
        sl = GetSearchPage(s)
        return sl

    @staticmethod
    def GetSearchOptions():
        return None
