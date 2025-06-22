from typing import List, Dict, Any, Optional
import json

from dao.collect.MacVodDao import MacVodDao
from dao.system.search_mac_vod import search_mac_vod_keyword, get_mac_vod_list_by_sort, get_mac_vod_list_by_tags, \
    get_relate_mac_vod_basic_info, get_search_tag_by_stat
from model.collect.categories import CategoryTree
from dao.collect.multiple_source import get_multiple_play
from dao.collect.categories import CategoryTreeService

from model.system.movies import MovieBasicInfo, MovieDetail
from model.system.response import Page
from plugin.common.conver.mac_vod import mac_vod_list_to_movie_basic_info_list, mac_vod_to_movie_detail
from plugin.db import redis_client
from config.data_config import INDEX_CACHE_KEY
from model.collect.collect_source import SourceGrade
from dao.collect.collect_source import FilmSourceService
from model.system.virtual_object import PlayLinkVo
from dao.system.manage import ManageService
from dao.system.movies import generate_hash_key
from dao.system.search import get_movie_list_by_pid, get_hot_movie_by_pid, get_movie_list_by_cid, \
    get_hot_movie_by_cid, get_search_infos_by_tags, \
    get_movie_list_by_sort, search_film_keyword, get_basic_info_by_search_info_list
import re


class IndexLogic:
    @staticmethod
    def index_page() -> Dict[str, Any]:
        # 首页数据处理逻辑
        info = redis_client.get(INDEX_CACHE_KEY)
        if info:
            return json.loads(info)
        info = {}
        # 1. 分类信息
        tree = CategoryTree(**{"id": 0, "name": "分类信息"})
        sys_tree = CategoryTreeService.get_category_tree()
        tree.children = [c for c in sys_tree.children if c.show]
        info["category"] = tree.model_dump()
        # 2. 首页内容
        content = []
        for c in tree.children:
            page = Page(pageSize=14, current=1)
            if c.children:
                movies = get_movie_list_by_pid(c.id, page)
                hot_movies = get_hot_movie_by_pid(c.id, page)
            else:
                movies = get_movie_list_by_cid(c.id, page)
                hot_movies = get_hot_movie_by_cid(c.id, page)
            movies_data = []
            if movies:
                movies_data = [m.model_dump() for m in movies]
            hot_movies_data = []
            if hot_movies:
                hot_movies_data = [h.model_dump() for h in hot_movies]
            item = {
                "nav": c.model_dump(),
                "movies": movies_data,
                "hot": hot_movies_data,
            }
            content.append(item)
        info["content"] = content
        # 3. 轮播
        info["banners"] = [b.model_dump() for b in ManageService.get_banners()]
        redis_client.set(INDEX_CACHE_KEY, json.dumps(info), ex=3600)
        return info

    @staticmethod
    def clear_index_cache():
        redis_client.delete("index_page_cache")

    @staticmethod
    def get_category_info() -> Dict[str, Any]:
        nav = {}
        tree = CategoryTreeService.get_category_tree()
        for t in tree.children:
            name = t.category.name
            if name in ["动漫", "动漫片"]:
                nav["cartoon"] = t.dict()
            elif name in ["电影", "电影片"]:
                nav["film"] = t.dict()
            elif name in ["连续剧", "电视剧"]:
                nav["tv"] = t.dict()
            elif name in ["综艺", "综艺片"]:
                nav["variety"] = t.dict()
        return nav

    @staticmethod
    def get_nav_category() -> List[Dict[str, Any]]:
        tree = CategoryTreeService.get_category_tree()
        cl = []
        for c in tree.children:
            if c.show:
                cl.append(c.model_dump())
        return cl

    @staticmethod
    def search_film_info(keyword: str, page: Page) -> list:
        """
        根据关键字和分页参数检索影片基本信息列表
        :param keyword: 检索关键字
        :param page: 当前页码
        :param pageSize: 每页数量
        :return: 影片基本信息列表
        """

        search_info_list = search_film_keyword(keyword, page)

        movie_basic_info_list = get_basic_info_by_search_info_list(search_info_list)
        return movie_basic_info_list

    @staticmethod
    def search_mac_vod_info(keyword: str, page: Page) -> list:
        """
        根据关键字和分页参数检索影片基本信息列表
        :param keyword: 检索关键字
        :param page: 当前页码
        :param pageSize: 每页数量
        :return: 影片基本信息列表
        """
        mac_vod_list = search_mac_vod_keyword(keyword, page)
        movie_basic_info_list = mac_vod_list_to_movie_basic_info_list(mac_vod_list)
        return movie_basic_info_list

    @staticmethod
    def get_film_category(id: int, id_type: str, page: int, pageSize: int) -> List[Dict[str, Any]]:
        page_obj = Page(pageSize=pageSize, current=page)
        if id_type == "pid":
            return [m.dict() for m in get_movie_list_by_pid(id, page_obj)]
        elif id_type == "cid":
            return [m.dict() for m in get_movie_list_by_cid(id, page_obj)]
        return []

    @staticmethod
    def get_pid_category(pid: int) -> Optional[Dict[str, Any]]:
        if pid == 0:
            pid = 4
        tree = CategoryTreeService.get_category_tree()
        for t in tree.children:
            if t.id == pid:
                return t.dict()
        return {
            "id": -1,
            "name": "",
            "pid": -1,
            "show": True,
        }

    # def search_tags(self, pid: int) -> Dict[str, Any]:
    #     return SearchTagsVO.get_search_tag(self.db, pid)

    @staticmethod
    def multiple_source(detail: MovieDetail) -> List[Dict[str, Any]]:
        master = FilmSourceService.get_collect_source_list_by_grade(SourceGrade.MasterCollect)

        play_list = [
            PlayLinkVo(**{
                "id": master[0].id,
                "name": master[0].name,
                "linkList": detail.playList[0]
            }).model_dump()
        ] if master and detail.playList else []
        names = set()
        if getattr(detail.descriptor, "dbId", 0) > 0:
            names.add(generate_hash_key(detail.descriptor.dbId))
        names.add(generate_hash_key(detail.name))

        names.add(generate_hash_key(re.sub(r"第一季$", "", detail.name)))
        if detail.descriptor.subTitle:
            for sep in [",", "/"]:
                if sep in detail.descriptor.subTitle:
                    for v in detail.descriptor.subTitle.split(sep):
                        names.add(generate_hash_key(v))
        sc = FilmSourceService.get_collect_source_list_by_grade(SourceGrade.SlaveCollect)
        for s in sc:
            for k in names:
                pl = get_multiple_play(s.id, k)
                if pl:
                    play_list.append(
                        PlayLinkVo(**{
                            "id": s.id, "name": s.name, "linkList": pl
                        }
                                   ).model_dump()
                    )
                    break
        return play_list

    @staticmethod
    def get_films_by_tags(tags: Dict[str, Any], page: Page) -> List[Dict[str, Any]]:
        search_info_list = get_search_infos_by_tags(tags, page)
        return get_basic_info_by_search_info_list(search_info_list)

    @staticmethod
    def get_mac_vod_list_by_tags(tags: Dict[str, Any], page: Page) -> List[Dict[str, Any]]:
        mac_vod_list = get_mac_vod_list_by_tags(tags, page)
        movie_basic_info_list = mac_vod_list_to_movie_basic_info_list(mac_vod_list)
        return movie_basic_info_list

    @staticmethod
    def search_tags(pid: int) -> Dict[str, Any]:
        """
        通过pid获取对应分类的搜索标签
        :param pid: 分类ID
        :return: 包含搜索标签的字典
        """
        # return get_search_tag(pid)
        return get_search_tag_by_stat(pid)

    @staticmethod
    def get_film_classify(pid: int, page: int, pageSize: int) -> Dict[str, Any]:
        page_obj = Page(**{"pageSize": pageSize, "current": page})
        return {
            "news": get_movie_list_by_sort(0, pid, page_obj),
            "top": get_movie_list_by_sort(1, pid, page_obj),
            "recent": get_movie_list_by_sort(2, pid, page_obj)
        }

    @staticmethod
    def get_mac_vod_list_classify(pid: int, page: int, pageSize: int) -> Dict[str, Any]:
        page_obj = Page(**{"pageSize": pageSize, "current": page})
        return {
            "news": get_mac_vod_list_by_sort(0, pid, page_obj),
            "top": get_mac_vod_list_by_sort(1, pid, page_obj),
            "recent": get_mac_vod_list_by_sort(2, pid, page_obj)
        }

    @staticmethod
    def get_film_detail(vod_id: int) -> Dict[str, Any]:
        """
        获取影片详情信息
        :param vod_id: 影片ID
        :return: 包含影片详情和播放源的字典
        """

        mac_vod = MacVodDao.select_mac_vod(vod_id)
        if not mac_vod:
            return {}
        movie_detail = mac_vod_to_movie_detail(mac_vod)

        # 查找其他站点的播放源
        play_list = IndexLogic.multiple_source(movie_detail)
        res = movie_detail.model_dump()
        res["list"] = play_list
        return res

    @staticmethod
    def relate_movie(movie_detail: MovieDetail, page: Page) -> List[MovieBasicInfo]:
        """
        根据当前影片信息匹配相关影片
        :param movie_detail: 影片详情对象
        :param page: 分页参数对象
        :return: 相关影片的基本信息列表
        """
        # search = SearchInfo(
        #     cid=movie_detail.cid,
        #     name=movie_detail.name,
        #     class_tag=movie_detail.descriptor.classTag,
        #     area=movie_detail.descriptor.area,
        #     language=movie_detail.descriptor.language,
        # )
        return get_relate_mac_vod_basic_info(movie_detail, page)
        # return get_relate_movie_basic_info(search, page)
