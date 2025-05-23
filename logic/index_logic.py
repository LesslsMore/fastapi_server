from typing import List, Dict, Any, Optional
from sqlmodel import select
import json
from model.system.categories import CategoryTree
from service.system.categories import get_category_tree

from model.system.movies import MovieBasicInfo, MovieDetail
from model.system.response import Page
from model.system.search import SearchInfo
from plugin.db import redis_client
from config.data_config import INDEX_CACHE_KEY
from plugin.db import get_db
from model.system.collect_source import SourceGrade
from service.system.collect_source import get_collect_source_list_by_grade
from model.system.virtual_object import PlayLinkVo
from service.system.manage import get_banners
from service.system.movies import generate_hash_key, get_detail_by_key
from service.system.search import get_movie_list_by_pid, get_hot_movie_by_pid, get_movie_list_by_cid, \
    get_hot_movie_by_cid, get_multiple_play, get_search_infos_by_tags, get_basic_info_by_search_infos, get_search_tag, \
    get_movie_list_by_sort, get_relate_movie_basic_info

from config.data_config import MOVIE_BASIC_INFO_KEY
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
        tree = CategoryTree(**{"id": 0, "name":"分类信息"})
        sys_tree = get_category_tree()
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
            item = {
                "nav": json.loads(c.model_dump_json()), 
                "movies": [json.loads(m.model_dump_json()) for m in movies], 
                "hot": [json.loads(h.model_dump_json()) for h in hot_movies]
            }
            content.append(item)
        info["content"] = content
        # 3. 轮播
        info["banners"] = [json.loads(b.model_dump_json()) for b in get_banners()]
        redis_client.set(INDEX_CACHE_KEY, json.dumps(info), ex=3600)
        return info


    @staticmethod
    def clear_index_cache():
        redis_client.delete("index_page_cache")

    @staticmethod
    def get_category_info() -> Dict[str, Any]:
        nav = {}
        tree = get_category_tree()
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
        tree = get_category_tree()
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

        sl = search_film_keyword(keyword, page)
        bl = []
        for s in sl:
            bl.append(get_basic_info_by_key(MOVIE_BASIC_INFO_KEY % (s.cid, s.mid)))
        return bl

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
        tree = get_category_tree()
        for t in tree.children:
            if t.id == pid:
                return t.dict()
        return None


    # def search_tags(self, pid: int) -> Dict[str, Any]:
    #     return SearchTagsVO.get_search_tag(self.db, pid)

    @staticmethod
    def multiple_source(detail: MovieDetail) -> List[Dict[str, Any]]:
        master = get_collect_source_list_by_grade(SourceGrade.MasterCollect)

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
        sc = get_collect_source_list_by_grade(SourceGrade.SlaveCollect)
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
    def get_films_by_tags(tags: Dict[str, Any], page: int, pageSize: int) -> List[Dict[str, Any]]:
        page_obj = Page(pageSize=pageSize, current=page)
        sl = get_search_infos_by_tags(tags, page_obj)
        return get_basic_info_by_search_infos(sl)

    @staticmethod
    def search_tags(pid: int) -> Dict[str, Any]:
        """
        通过pid获取对应分类的搜索标签
        :param pid: 分类ID
        :return: 包含搜索标签的字典
        """
        return get_search_tag(pid)
    @staticmethod
    def get_film_classify(pid: int, page: int, pageSize: int) -> Dict[str, Any]:
        page_obj = Page(**{"pageSize": pageSize, "current": page})
        return {
            "news": get_movie_list_by_sort(0, pid, page_obj),
            "top": get_movie_list_by_sort(1, pid, page_obj),
            "recent": get_movie_list_by_sort(2, pid, page_obj)
        }

    @staticmethod
    def get_film_detail(id: int) -> Dict[str, Any]:
        """
        获取影片详情信息
        :param id: 影片ID
        :return: 包含影片详情和播放源的字典
        """
        # 通过ID获取影片搜索信息
        session = get_db()
        search = session.exec(
            select(SearchInfo).where(SearchInfo.mid == id)
        ).first()
        if not search:
            return {}
            
        # 获取Redis中的完整影视信息
        detail = get_detail_by_key(f"MovieDetail:Cid{search.cid}:Id{search.mid}")
        if not detail:
            return {}
            
        # 查找其他站点的播放源
        play_list = IndexLogic.multiple_source(detail)
        res = detail.model_dump()
        res["list"] = play_list
        return res

    @staticmethod
    def relate_movie(detail: MovieDetail, page: Page) -> List[MovieBasicInfo]:
        """
        根据当前影片信息匹配相关影片
        :param detail: 影片详情对象
        :param page: 分页参数对象
        :return: 相关影片的基本信息列表
        """
        search = SearchInfo(
            cid=detail["cid"],
            name=detail["name"],
            class_tag=detail['descriptor']["classTag"],
            area=detail['descriptor']["area"],
            language=detail['descriptor']["language"]
        )
        return get_relate_movie_basic_info(search, page)