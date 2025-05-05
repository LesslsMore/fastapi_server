from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
import redis
import json
from model.system.categories import Category, CategoryTree
from model.service.categories import get_category_tree

from model.system.movies import MovieBasicInfo, MovieDetail
from model.system.response import Page
from model.system.manage import Banner
from model.service.manage import get_banners
from model.system.search import SearchInfo
from model.service.search import get_relate_movie_basic_info, get_multiple_play, get_movie_list_by_sort, get_search_infos_by_tags, get_basic_info_by_search_infos, get_search_tag, get_movie_list_by_pid, get_movie_list_by_cid, get_hot_movie_by_pid, get_hot_movie_by_cid

from plugin.db.redis_client import redis_client, init_redis_conn
from config.data_config import INDEX_CACHE_KEY

from model.service.movies import get_detail_by_key, generate_hash_key
from plugin.db.mysql import get_db_engine, get_db
from model.system.collect_source import FilmSource, SourceGrade
from model.service.collect_source import get_collect_source_list_by_grade
from model.system.virtual_object import PlayLinkVo




class IndexLogic:
    def __init__(self, db_session: Session, redis_client: redis.Redis):
        self.db = db_session
        self.redis = redis_client
        
    def index_page(self) -> Dict[str, Any]:
        # 首页数据处理逻辑
        redis = redis_client or init_redis_conn()

        cache_key = INDEX_CACHE_KEY
        info = redis.get(cache_key)
        if info:
            return eval(info)
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
        redis.set(cache_key, str(info), ex=3600)
        return info



    def clear_index_cache(self):
        self.redis.delete("index_page_cache")

    def get_category_info(self) -> Dict[str, Any]:
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

    def get_nav_category(self) -> List[Dict[str, Any]]:
        tree = get_category_tree()
        return [Category(**c.model_dump()).model_dump() for c in tree.children if c.show]

    def search_film_info(self, keyword: str, page: Page) -> list:
        """
        根据关键字和分页参数检索影片基本信息列表
        :param keyword: 检索关键字
        :param page: 当前页码
        :param pageSize: 每页数量
        :return: 影片基本信息列表
        """
        from model.service.search import search_film_keyword
        from model.service.movies import get_basic_info_by_key
        from config.data_config import MOVIE_BASIC_INFO_KEY
        sl = search_film_keyword(keyword, page)
        bl = []
        for s in sl:
            bl.append(get_basic_info_by_key(MOVIE_BASIC_INFO_KEY % (s.cid, s.mid)))
        return bl

    def get_film_category(self, id: int, id_type: str, page: int, pageSize: int) -> List[Dict[str, Any]]:
        page_obj = Page(pageSize=pageSize, current=page)
        if id_type == "pid":
            return [m.dict() for m in MovieBasicInfo.get_movie_list_by_pid(self.db, id, page_obj)]
        elif id_type == "cid":
            return [m.dict() for m in MovieBasicInfo.get_movie_list_by_cid(self.db, id, page_obj)]
        return []

    def get_pid_category(self, pid: int) -> Optional[Dict[str, Any]]:
        tree = get_category_tree()
        for t in tree.children:
            if t.id == pid:
                return t.dict()
        return None


    # def search_tags(self, pid: int) -> Dict[str, Any]:
    #     return SearchTagsVO.get_search_tag(self.db, pid)

    def multiple_source(self, detail: MovieDetail) -> List[Dict[str, Any]]:
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
        import re
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

    def get_films_by_tags(self, tags: Dict[str, Any], page: int, pageSize: int) -> List[Dict[str, Any]]:
        page_obj = Page(pageSize=pageSize, current=page)
        sl = get_search_infos_by_tags(tags, page_obj)
        return get_basic_info_by_search_infos(sl)
        
    def search_tags(self, pid: int) -> Dict[str, Any]:
        """
        通过pid获取对应分类的搜索标签
        :param pid: 分类ID
        :return: 包含搜索标签的字典
        """
        return get_search_tag(pid)

    def get_film_classify(self, pid: int, page: int, pageSize: int) -> Dict[str, Any]:
        page_obj = Page(**{"pageSize": pageSize, "current": page})
        return {
            "news": get_movie_list_by_sort(0, pid, page_obj),
            "top": get_movie_list_by_sort(1, pid, page_obj),
            "recent": get_movie_list_by_sort(2, pid, page_obj)
        }
        
    def get_film_detail(self, id: int) -> Dict[str, Any]:
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
        play_list = self.multiple_source(detail)
        res = detail.model_dump()
        res["list"] = play_list
        return res

    def relate_movie(self, detail: MovieDetail, page: Page) -> List[MovieBasicInfo]:
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