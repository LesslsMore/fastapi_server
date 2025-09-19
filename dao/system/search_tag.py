from datetime import datetime
from datetime import datetime
from typing import List

from config.data_config import SEARCH_TAG
from dao.collect.MacVodDao import MacVodDao
from dao.collect.categories import CategoryTreeService


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
        if isinstance(tag, tuple):
            tag = tag[1]
        if ":" in tag:
            name, value = tag.split(":", 1)
            result.append({"Name": name, "Value": value})
        else:
            result.append({"Name": tag, "Value": tag})
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

        # for t in CategoryTreeService.get_children_tree(search.pid):
        #     redis_client.zadd(tag_key, {f"{t.name}:{t.id}": -t.id})
    elif t in ["Plot", "Area", "Language", "Year", "Initial", "Sort"]:
        tag_key = SEARCH_TAG % (pid, t)
        if t == "Plot":
            tags = MacVodDao.count_vod_class_tags(pid)
        elif t == "Area":
            tags = MacVodDao.count_vod_key_tags('vod_area', ' / ', pid)
        elif t == "Language":
            tags = MacVodDao.count_vod_key_tags('vod_lang', ',', pid)
        elif t == "Year":
            tags = []
            current_year = datetime.now().year
            for i in range(12):
                tags.append((current_year - i, f"{current_year - i}:{current_year - i}"))
        elif t == "Initial":
            tags = []
            for i in range(65, 91):
                tags.append((90 - i, f"{chr(i)}:{chr(i)}"))
        elif t == "Sort":
            tags = [
                (3, "时间排序:update_stamp"),
                (2, "人气排序:hits"),
                (1, "评分排序:score"),
                (0, "最新上映:release_stamp")
            ]
    return tags
