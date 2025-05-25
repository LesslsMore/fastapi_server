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
from service.collect.movie_dao import get_movie_basic_info
from service.system.categories import get_children_tree


def get_basic_info_by_search_infos(search_info_list: List[SearchInfo]) -> List[MovieBasicInfo]:
    movie_basic_info_list = []
    for search_info in search_info_list:
        movie_basic_info = get_movie_basic_info(search_info)
        if movie_basic_info:
            movie_basic_info_list.append(movie_basic_info)
    return movie_basic_info_list


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


# 重置Search表
def reset_search_table():
    session = get_session()
    session.execute(text('DROP TABLE IF EXISTS search_info'))
    session.commit()


# 清空附加播放源信息
def del_mt_play(keys: List[str]):
    if keys:
        redis_client.delete(*keys)


# 批量处理标签
def batch_handle_search_tag(search_info_list: List[SearchInfo]):
    for search_info in search_info_list:
        save_search_tag(search_info)


def exist_search_table() -> bool:
    """
    判断是否存在Search Table
    """
    session = get_session()
    result = session.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'search_info'
    )
    """).fetchone()
    return result[0]


# 判断是否存在影片检索信息
def exist_search_info(mid: int):
    session = get_session()
    result = session.execute(text("SELECT COUNT(*) FROM search_info WHERE mid=:mid"), {"mid": mid})
    return result.scalar() > 0


# 截断search_info表
def truncate_search_table():
    session = get_session()
    session.execute(text('TRUNCATE TABLE search_info'))
    session.commit()


# 影片检索相关的其他函数
def get_search_infos_by_tags(st: dict, page: Page) -> Optional[List[SearchInfo]]:
    """
    根据标签条件筛选影片信息
    :param st: 搜索标签参数字典
    :param page: 分页参数
    :return: 符合条件的SearchInfo列表
    """
    try:
        session = get_session()
        query = select(SearchInfo)

        # 处理各标签条件
        if st.get('Pid'):
            query = query.where(SearchInfo.pid == st['Pid'])
        if st.get('Cid'):
            query = query.where(SearchInfo.cid == st['Cid'])
        if st.get('Year'):
            query = query.where(SearchInfo.year == st['Year'])

        # 处理特殊标签条件
        if st.get('Area') == '其它':
            tags = get_tags_by_title(st['Pid'], 'Area')
            exclude_areas = [t.split(':')[1] for t in tags]
            query = query.where(SearchInfo.area.not_in(exclude_areas))
        elif st.get('Area'):
            query = query.where(SearchInfo.area == st['Area'])

        if st.get('Language') == '其它':
            tags = get_tags_by_title(st['Pid'], 'Language')
            exclude_langs = [t.split(':')[1] for t in tags]
            query = query.where(SearchInfo.language.not_in(exclude_langs))
        elif st.get('Language'):
            query = query.where(SearchInfo.language == st['Language'])

        if st.get('Plot') == '其它':
            tags = get_tags_by_title(st['Pid'], 'Plot')
            exclude_plots = [t.split(':')[1] for t in tags]
            for plot in exclude_plots:
                query = query.where(SearchInfo.class_tag.not_like(f'%{plot}%'))
        elif st.get('Plot'):
            query = query.where(SearchInfo.class_tag.like(f'%{st["Plot"]}%'))

        # 处理排序
        if st.get('Sort') == 'release_stamp':
            query = query.order_by(SearchInfo.year.desc(), SearchInfo.release_stamp.desc())
        elif st.get('Sort'):
            query = query.order_by(getattr(SearchInfo, st['Sort']).desc())

        # 添加分页
        query = query.offset((page.current - 1) * page.pageSize).limit(page.pageSize)

        search_infos = session.exec(query).all()
        return search_infos
    except Exception as e:
        print(f"查询失败: {e}")
        return None


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
        from .categories import get_children_tree
        children = get_children_tree(pid)
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


def get_movie_list_by_pid(pid: int, page: Page) -> Optional[List[MovieBasicInfo]]:
    """
    通过Pid分类ID获取对应影片的数据信息
    :param pid: 分类ID
    :param page: 分页参数
    :return: 影片基本信息列表
    """
    try:
        session = get_session()
        # 计算总数
        count = session.exec(select(func.count()).select_from(SearchInfo).where(SearchInfo.pid == pid)).one()
        page.total = count
        page.pageCount = (page.total + page.pageSize - 1) // page.pageSize

        # 查询数据
        query = select(SearchInfo).where(SearchInfo.pid == pid).order_by(SearchInfo.update_stamp.desc()) \
            .offset((page.current - 1) * page.pageSize).limit(page.pageSize)
        search_infos = session.exec(query).all()

        return get_basic_info_by_search_infos(search_infos)
    except Exception as e:
        print(f"查询失败: {e}")
        return None


def get_movie_list_by_cid(cid: int, page: Page) -> Optional[List[MovieBasicInfo]]:
    """
    通过Cid查找对应的影片分页数据
    :param cid: 分类ID
    :param page: 分页参数
    :return: 影片基本信息列表
    """
    try:
        session = get_session()
        # 计算总数
        count = session.exec(select(func.count()).select_from(SearchInfo).where(SearchInfo.cid == cid)).one()
        page.total = count
        page.pageCount = (page.total + page.pageSize - 1) // page.pageSize

        # 查询数据
        query = select(SearchInfo).where(SearchInfo.cid == cid).order_by(SearchInfo.update_stamp.desc()) \
            .offset((page.current - 1) * page.pageSize).limit(page.pageSize)
        search_infos = session.exec(query).all()

        return get_basic_info_by_search_infos(search_infos)
    except Exception as e:
        print(f"查询失败: {e}")
        return None


def get_hot_movie_by_pid(pid: int, page: Page) -> Optional[List[SearchInfo]]:
    """
    获取Pid指定类别的热门影片
    :param pid: 分类ID
    :param page: 分页参数
    :return: 搜索信息列表
    """
    try:
        session = get_session()
        # 当前时间偏移一个月
        t = datetime.now() - timedelta(days=30)

        query = select(SearchInfo).where(
            SearchInfo.pid == pid,
            SearchInfo.update_stamp > t.timestamp()
        ).order_by(SearchInfo.year.desc(), SearchInfo.hits.desc()) \
            .offset((page.current - 1) * page.pageSize).limit(page.pageSize)

        return session.exec(query).all()
    except Exception as e:
        print(f"查询失败: {e}")
        return None


def get_hot_movie_by_cid(cid: int, page: Page) -> Optional[List[SearchInfo]]:
    """
    获取当前分类下的热门影片
    :param cid: 分类ID
    :param page: 分页参数
    :return: 搜索信息列表
    """
    try:
        session = get_session()
        # 当前时间偏移一个月
        t = datetime.now() - timedelta(days=30)

        query = select(SearchInfo).where(
            SearchInfo.cid == cid,
            SearchInfo.update_stamp > t.timestamp()
        ).order_by(SearchInfo.year.desc(), SearchInfo.hits.desc()) \
            .offset((page.current - 1) * page.pageSize).limit(page.pageSize)

        return session.exec(query).all()
    except Exception as e:
        print(f"查询失败: {e}")
        return None


def get_movie_list_by_sort(sort_type: int, pid: int, page: Page) -> Optional[List[MovieBasicInfo]]:
    """
    根据排序类型返回对应分类的影片基本信息
    :param sort_type: 排序类型 0-最新上映 1-热度排行 2-最近更新
    :param pid: 分类ID
    :param page: 分页参数
    :param session: 数据库会话(通过依赖注入获取)
    :return: 影片基本信息列表
    """
    query = select(SearchInfo).where(SearchInfo.pid == pid)

    # 根据排序类型添加排序条件
    if sort_type == 0:
        query = query.order_by(SearchInfo.release_stamp.desc())
    elif sort_type == 1:
        query = query.order_by(SearchInfo.hits.desc())
    elif sort_type == 2:
        query = query.order_by(SearchInfo.update_stamp.desc())

    # 添加分页限制
    query = query.offset((page.current - 1) * page.pageSize).limit(page.pageSize)

    try:
        session = get_session()
        search_infos = session.exec(query).all()
        return get_basic_info_by_search_infos(search_infos)
    except Exception as e:
        print(f"查询失败: {e}")
        return None


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


def get_multiple_play(site_id: str, key: str) -> Optional[List[MovieUrlInfo]]:
    """
    通过影片名hash值匹配播放源
    :param site_id: 站点ID
    :param key: 影片名hash值
    :return: 播放源信息列表
    """
    try:
        data = redis_client.hget(MULTIPLE_SITE_DETAIL % (site_id), key)
        if data:
            play_list = json.loads(data)
            return [MovieUrlInfo(**item) for item in play_list]
        return None
    except Exception as e:
        print(f"获取播放源失败: {e}")
        return None


def get_relate_movie_basic_info(search: SearchInfo, page: Page) -> Optional[List[MovieBasicInfo]]:
    """
    根据当前影片信息匹配相关影片
    1. 分类cid
    2. 影片名称相似（去除季、数字、剧场版等）
    3. class_tag（剧情内容）模糊匹配
    4. area、language可扩展
    :param search: SearchInfo对象
    :param page: 分页参数
    :return: 相关影片的基本信息列表
    """
    import re
    from sqlmodel import or_, select
    try:
        session = get_session()
        # 确保分页参数 current 至少为 1
        page.current = max(1, page.current)
        # 处理影片名称，去除季、数字、剧场版等
        name = re.sub(r'(第.{1,3}季.*)|([0-9]{1,3})|(剧场版)|([\s\S]*$)|(之.*)|([^u4e00-u9fa5\w].*)', '', search.name)
        # 如果处理后长度没变且大于10，做截断
        if len(name) == len(search.name) and len(name) > 10:
            name = name[:((len(name) // 5) * 3)]
        # 名称相似匹配
        query = select(SearchInfo).where(
            SearchInfo.cid == search.cid,
            or_(SearchInfo.name.contains(name), SearchInfo.sub_title.contains(name))
        )
        # 排除自身mid
        if getattr(search, 'mid', None):
            query = query.where(SearchInfo.mid != search.mid)
        # 剧情标签模糊匹配
        class_tag = (search.class_tag or '').replace(' ', '')
        tag_conditions = []
        if ',' in class_tag:
            for t in class_tag.split(','):
                tag_conditions.append(SearchInfo.class_tag.contains(t))
        elif '/' in class_tag:
            for t in class_tag.split('/'):
                tag_conditions.append(SearchInfo.class_tag.contains(t))
        elif class_tag:
            tag_conditions.append(SearchInfo.class_tag.contains(class_tag))
        if tag_conditions:
            query = query.where(or_(*tag_conditions))
        # 分页
        query = query.offset((page.current - 1) * page.pageSize).limit(page.pageSize)
        search_infos = session.exec(query).all()
        return get_basic_info_by_search_infos(search_infos)
    except Exception as e:
        print(f"查询相关影片失败: {e}")
        return None


def search_film_keyword(keyword: str, page: Page) -> Optional[List[SearchInfo]]:
    """
    根据关键字对影片名称和副标题进行模糊查询，支持分页，返回符合条件的影片信息列表。
    :param keyword: 搜索关键字
    :param page: 分页参数
    :return: SearchInfo列表
    """
    try:
        session = get_session()
        # 统计满足条件的数据量
        count = session.exec(
            select(func.count()).select_from(SearchInfo)
            .where(
                or_(
                    SearchInfo.name.contains(keyword),
                    SearchInfo.sub_title.contains(keyword)
                )
            )
        ).one()
        page.total = count
        page.pageCount = (page.total + page.pageSize - 1) // page.pageSize
        # 查询满足条件的数据
        query = (
            select(SearchInfo)
            .where(
                or_(
                    SearchInfo.name.contains(keyword),
                    SearchInfo.sub_title.contains(keyword)
                )
            )
            .order_by(SearchInfo.year.desc(), SearchInfo.update_stamp.desc())
            .offset((page.current - 1) * page.pageSize)
            .limit(page.pageSize)
        )
        search_list = session.exec(query).all()
        return search_list
    except Exception as e:
        print(f"查询失败: {e}")
        return None


def save_search_info(search_info: SearchInfo) -> None:
    # Save search information to the database
    session = get_session()
    if not exist_search_info(search_info.mid):
        session.add(search_info)
        session.commit()
        batch_handle_search_tag([search_info])
    else:
        session.query(SearchInfo).filter(SearchInfo.mid == search_info.mid).update({
            SearchInfo.update_stamp: search_info.update_stamp,
            SearchInfo.hits: search_info.hits,
            SearchInfo.state: search_info.state,
            SearchInfo.remarks: search_info.remarks,
            SearchInfo.score: search_info.score,
            SearchInfo.release_stamp: search_info.release_stamp
        })
        session.commit()


def sync_search_info(model: int) -> None:
    if model == 0:
        reset_search_table()
        search_info_to_mdb(model)
        add_search_index()
    elif model == 1:
        search_info_to_mdb(model)


def exist_search_info(mid: int) -> bool:
    # Check if search information exists in the database
    session = get_session()
    count = session.query(SearchInfo).filter(SearchInfo.mid == mid).count()
    return count > 0


def truncate_search_table() -> None:
    # Truncate the search_info table
    session = get_session()
    session.execute('TRUNCATE TABLE search_info')
    session.commit()


# Additional functions can be implemented similarly based on the Go code
def search_info_to_mdb(model: int) -> None:
    count = redis_client.zcard(SEARCH_INFO_TEMP)
    if count <= 0:
        return

    list_ = redis_client.zpopmax(SEARCH_INFO_TEMP, count)
    if not list_:
        return

    sl = []
    for member, score in list_:
        info = SearchInfo(**json.loads(member))
        sl.append(info)

    if model == 0:
        batch_save(sl)
    elif model == 1:
        batch_save_or_update(sl)

    search_info_to_mdb(model)


def batch_save(search_info_list: List[SearchInfo]) -> None:
    session = get_session()
    try:
        session.bulk_save_objects(search_info_list)
        batch_handle_search_tag(search_info_list)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"批量保存失败: {e}")
        logging.error(f"批量保存失败: {e}")


def batch_save_or_update(list_: List[SearchInfo]) -> None:
    session = get_session()
    for info in list_:
        existing_info = session.exec(select(SearchInfo).where(SearchInfo.mid == info.mid)).first()
        if existing_info:
            try:
                session.exec(
                    update(SearchInfo)
                    .where(SearchInfo.mid == info.mid)
                    .values(
                        update_stamp=info.update_stamp,
                        hits=info.hits,
                        state=info.state,
                        remarks=info.remarks,
                        score=info.score,
                        release_stamp=info.release_stamp
                    )
                )
            except Exception as e:
                session.rollback()
                logging.error(f"batch_save_or_update: {e}")
        else:
            try:
                session.add(info)
                batch_handle_search_tag([info])
            except Exception as e:
                session.rollback()
                logging.error(f"batch_handle_search_tag: {e}")
    session.commit()


def add_search_index() -> None:
    session = get_session()
    session.exec(text("CREATE UNIQUE INDEX idx_mid ON search_info (mid)"))
    session.exec(text("CREATE INDEX idx_time ON search_info (update_stamp DESC)"))
    session.exec(text("CREATE INDEX idx_hits ON search_info (hits DESC)"))
    session.exec(text("CREATE INDEX idx_score ON search_info (score DESC)"))
    session.exec(text("CREATE INDEX idx_release ON search_info (release_stamp DESC)"))
    session.exec(text("CREATE INDEX idx_year ON search_info (year DESC)"))


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


def get_search_info(id):
    # 通过ID获取影片搜索信息
    session = get_session()
    search_info = session.exec(
        select(SearchInfo).where(SearchInfo.mid == id)
    ).first()
    return search_info


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
                for t in get_children_tree(search.pid):
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
