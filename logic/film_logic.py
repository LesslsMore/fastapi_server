from typing import List

from model.system.search import SearchInfo
from model.system.virtual_object import SearchVo
from service.system.categories import CategoryTreeService
from service.system.search import GetSearchPage
from service.system.user_service import get_user_by_id, get_user_by_name_or_email
from plugin.common.util.string_util import password_encrypt
from plugin.middleware.jwt_token import gen_token, save_user_token


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
