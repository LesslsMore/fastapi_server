import logging
from typing import List, Optional, Any
from sqlmodel import SQLModel
import json
from plugin.db import redis_client, pg_engine
from sqlalchemy import create_engine, text, update
from config.data_config import MULTIPLE_SITE_DETAIL, SEARCH_INFO_TEMP, SEARCH_TITLE, SEARCH_TAG
import re
from datetime import datetime, timedelta
from model.system.movies import MovieBasicInfo, MovieUrlInfo
from model.system.search import SearchInfo

from typing import List, Optional
from sqlmodel import Session, select, func, desc, or_, and_
from fastapi import Depends
from plugin.db import get_session
from model.system.response import Page
from service.collect.movie_dao import get_movie_basic_info, select_movie_basic_info_list
from service.system.categories import get_children_tree, CategoryTreeService


# 删除所有库存数据
def film_zero():
    keys_patterns = [
        'MovieBasicInfoKey*', 'MovieDetail*', 'MultipleSource*', 'OriginalResource*', 'Search*'
    ]
    for pattern in keys_patterns:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    session = get_session()
    session.execute(text('TRUNCATE TABLE search_info'))
    session.commit()


# 清空附加播放源信息
def del_mt_play(keys: List[str]):
    if keys:
        redis_client.delete(*keys)


# 批量处理标签
def batch_handle_search_tag(search_info_list: List[SearchInfo]):
    for search_info in search_info_list:
        save_search_tag(search_info)


def get_search_tag(pid: int) -> dict:
    """
    通过影片分类Pid返回对应分类的tag信息
    :param pid: 分类ID
    :return: 包含标签信息的字典
    """
    result = {}

    # 获取标题信息
    key = SEARCH_TITLE % (pid)
    titles = redis_client.hgetall(key)
    result["titles"] = titles

    # 处理标签信息
    tag_map = {}
    for title in titles:
        tags = get_tags_by_title(pid, title)
        tag_map[title] = handle_tag_str(title, tags)

    result["tags"] = tag_map
    result["sortList"] = ["Category", "Plot", "Area", "Language", "Year", "Sort"]

    return result


def handle_tag_str(title: str, tags: List[str]) -> List[dict]:
    """
    处理标签字符串格式转换
    :param title: 标签类型
    :param tags: 标签列表
    :return: 格式化后的标签列表
    """
    result = []
    if title.lower() != "sort":
        result.append({"Name": "全部", "Value": ""})

    for tag in tags:
        if ":" in tag:
            name, value = tag.split(":", 1)
            result.append({"Name": name, "Value": value})

    if title.lower() not in ["sort", "year", "category"]:
        result.append({"Name": "其它", "Value": "其它"})

    return result


def get_tags_by_title(pid: int, t: str) -> List[str]:
    """
    返回Pid和title对应的用于检索的tag
    :param pid: 分类ID
    :param t: 标题类型(Category/Plot/Area/Language/Year/Initial/Sort)
    :return: 标签列表
    """
    tags = []
    # 过滤分类tag
    if t == "Category":
        children = CategoryTreeService.get_children_tree(pid)
        if children:
            for c in children:
                if c.show:
                    tags.append(f"{c.name}:{c.id}")
    elif t in ["Plot", "Area", "Language", "Year", "Initial", "Sort"]:
        tag_key = SEARCH_TAG % (pid, t)
        if t == "Plot":
            tags = redis_client.zrevrange(tag_key, 0, 10)
        elif t == "Area":
            tags = redis_client.zrevrange(tag_key, 0, 11)
        elif t == "Language":
            tags = redis_client.zrevrange(tag_key, 0, 6)
        else:
            tags = redis_client.zrevrange(tag_key, 0, -1)
    return tags


def handle_search_tags(pre_tags: str, k: str):
    # 先处理字符串中的空白符 然后对处理前的tag字符串进行分割
    pre_tags = re.sub(r'[\s\n\r]+', '', pre_tags)

    def f(sep: str):
        for t in pre_tags.split(sep):
            # 获取 tag对应的score
            score = redis_client.zscore(k, f"{t}:{t}") or 0
            # 在原score的基础上+1 重新存入redis中
            redis_client.zadd(k, {f"{t}:{t}": score + 1})

    if '/' in pre_tags:
        f('/')
    elif ',' in pre_tags:
        f(',')
    elif '，' in pre_tags:
        f('，')
    elif '、' in pre_tags:
        f('、')
    else:
        # 获取 tag对应的score
        if len(pre_tags) == 0:
            pass
        elif pre_tags == "其它":
            redis_client.zadd(k, {f"{pre_tags}:{pre_tags}": 0})
        else:
            score = redis_client.zscore(k, f"{pre_tags}:{pre_tags}") or 0
            redis_client.zadd(k, {f"{pre_tags}:{pre_tags}": score + 1})


def save_search_tag(search: SearchInfo):
    try:
        key = SEARCH_TITLE % (search.pid)
        search_map = redis_client.hgetall(key)
        if not search_map:
            search_map = {
                "Category": "类型",
                "Plot": "剧情",
                "Area": "地区",
                "Language": "语言",
                "Year": "年份",
                "Initial": "首字母",
                "Sort": "排序"
            }
            redis_client.hmset(key, search_map)

        for k in search_map.keys():
            tag_key = SEARCH_TAG % (search.pid, k)
            tag_count = redis_client.zcard(tag_key)
            if k == "Category" and tag_count == 0:
                for t in CategoryTreeService.get_children_tree(search.pid):
                    redis_client.zadd(tag_key, {f"{t.name}:{t.id}": -t.id})
            elif k == "Year" and tag_count == 0:
                current_year = datetime.now().year
                for i in range(12):
                    redis_client.zadd(tag_key, {f"{current_year - i}:{current_year - i}": current_year - i})
            elif k == "Initial" and tag_count == 0:
                for i in range(65, 91):
                    redis_client.zadd(tag_key, {f"{chr(i)}:{chr(i)}": 90 - i})
            elif k == "Sort" and tag_count == 0:
                tags = [
                    (3, "时间排序:update_stamp"),
                    (2, "人气排序:hits"),
                    (1, "评分排序:score"),
                    (0, "最新上映:release_stamp")
                ]
                mapping = {}
                for score, member in tags:
                    mapping[member] = score
                redis_client.zadd(tag_key, mapping=mapping)
            elif k == "Plot":
                handle_search_tags(search.class_tag, tag_key)
            elif k == "Area":
                handle_search_tags(search.area, tag_key)
            elif k == "Language":
                handle_search_tags(search.language, tag_key)
    except Exception as e:
        logging.error('save_search_tag: {}', e)


def remove_cache(key: str) -> bool:
    """
    删除Redis中的缓存数据
    :param key: 缓存键
    :return: 是否删除成功
    """
    try:
        return redis_client.delete(key) > 0
    except Exception as e:
        print(f"删除缓存数据失败: {e}")
        return False


def data_cache(key: str, data: Any, expire: int = 0) -> bool:
    """
    缓存数据到Redis
    :param key: 缓存键
    :param data: 要缓存的数据
    :param expire: 过期时间(秒)
    :return: 是否缓存成功
    """
    try:
        if isinstance(data, (dict, list)):
            data = json.dumps(data, ensure_ascii=False)
        if expire > 0:
            redis_client.setex(key, expire, data)
        else:
            redis_client.set(key, data)
        return True
    except Exception as e:
        print(f"缓存数据失败: {e}")
        return False


def get_cache_data(key: str) -> Optional[Any]:
    """
    从Redis获取缓存数据
    :param key: 缓存键
    :return: 缓存数据
    """
    try:
        data = redis_client.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None
    except Exception as e:
        print(f"获取缓存数据失败: {e}")
        return None
