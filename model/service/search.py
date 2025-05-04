from typing import List, Optional, Any
from sqlmodel import SQLModel
import json
from plugin.db.redis_client import redis_client, init_redis_conn
from sqlalchemy import create_engine, text
from config.data_config import MULTIPLE_SITE_DETAIL, SEARCH_INFO_TEMP, SEARCH_TITLE, SEARCH_TAG, MOVIE_BASIC_INFO_KEY, MOVIE_DETAIL_KEY
import re
from datetime import datetime, timedelta
from model.system.movies import MovieBasicInfo, MovieUrlInfo
from model.system.search import SearchInfo
from model.service.movies import get_basic_info_by_search_infos
from typing import List, Optional
from sqlmodel import Session, select, func, desc, or_, and_
from fastapi import Depends
from plugin.db.mysql import get_db_engine, get_db
from plugin.db.mysql import db_engine
from model.system.response import Page

# 批量保存检索信息到redis
def rdb_save_search_info(list_: List[SQLModel]):
    members = []
    for s in list_:
        member = json.dumps(s.dict(), ensure_ascii=False)
        members.append({
            'score': float(s.mid),
            'member': member
        })
    if members:
        redis_client.zadd(SEARCH_INFO_TEMP, {m['member']: m['score'] for m in members})

# 删除所有库存数据
def film_zero(db_engine):
    keys_patterns = [
        'MovieBasicInfoKey*', 'MovieDetail*', 'MultipleSource*', 'OriginalResource*', 'Search*'
    ]
    for pattern in keys_patterns:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    with db_engine.connect() as conn:
        conn.execute(text('TRUNCATE TABLE search_info'))
        conn.commit()

# 重置Search表
def reset_search_table(db_engine):
    with db_engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS search_info'))
        conn.commit()

# 清空附加播放源信息
def del_mt_play(keys: List[str]):
    if keys:
        redis_client.delete(*keys)

# 标签处理相关
def save_search_tag(search: SQLModel):
    key = SEARCH_TITLE.format(search.pid)
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
    for k in search_map:
        tag_key = SEARCH_TAG.format(search.pid, k)
        tag_count = redis_client.zcard(tag_key)
        if k == "Category" and tag_count == 0:
            from .categories import get_children_tree
            children = get_children_tree(search.pid)
            if children:
                for t in children:
                    redis_client.zadd(tag_key, {f"{t.name}:{t.id}": -t.id})
        elif k == "Year" and tag_count == 0:
            current_year = datetime.now().year
            for i in range(12):
                y = current_year - i
                redis_client.zadd(tag_key, {f"{y}:{y}": y})
        elif k == "Initial" and tag_count == 0:
            for i in range(65, 91):
                c = chr(i)
                redis_client.zadd(tag_key, {f"{c}:{c}": 90 - i})
        elif k == "Sort" and tag_count == 0:
            tags = {
                "时间排序:update_stamp": 3,
                "人气排序:hits": 2,
                "评分排序:score": 1,
                "最新上映:release_stamp": 0
            }
            redis_client.zadd(tag_key, tags)
        elif k == "Plot":
            handle_search_tags(search.class_tag, tag_key)
        elif k == "Area":
            handle_search_tags(search.area, tag_key)
        elif k == "Language":
            handle_search_tags(search.language, tag_key)

# 处理标签字符串
def handle_search_tags(pre_tags: Optional[str], k: str):
    if not pre_tags:
        return
    pre_tags = re.sub(r"[\s\n\r]+", "", pre_tags)
    def add_tag(tag):
        score = redis_client.zscore(k, f"{tag}:{tag}") or 0
        redis_client.zadd(k, {f"{tag}:{tag}": score + 1})
    if "/" in pre_tags:
        for t in pre_tags.split("/"):
            add_tag(t)
    elif "," in pre_tags:
        for t in pre_tags.split(","):
            add_tag(t)
    elif "，" in pre_tags:
        for t in pre_tags.split("，"):
            add_tag(t)
    elif "、" in pre_tags:
        for t in pre_tags.split("、"):
            add_tag(t)
    else:
        if pre_tags == "其它":
            redis_client.zadd(k, {"其它:其它": 0})
        elif pre_tags:
            add_tag(pre_tags)

# 批量处理标签
def batch_handle_search_tag(infos: List[SQLModel]):
    for info in infos:
        save_search_tag(info)

# 批量保存影片search信息
def batch_save(db_engine, list_: List[SQLModel]):
    with db_engine.begin() as conn:
        for s in list_:
            conn.execute(text(
                """
                INSERT INTO search_info (mid, cid, pid, name, sub_title, c_name, class_tag, area, language, year, initial, score, update_stamp, hits, state, remarks, release_stamp)
                VALUES (:mid, :cid, :pid, :name, :sub_title, :c_name, :class_tag, :area, :language, :year, :initial, :score, :update_stamp, :hits, :state, :remarks, :release_stamp)
                """), s.dict())
        batch_handle_search_tag(list_)

# 批量保存或更新
def batch_save_or_update(db_engine, list_: List[SQLModel]):
    with db_engine.begin() as conn:
        for s in list_:
            result = conn.execute(text("SELECT COUNT(*) FROM search_info WHERE mid=:mid"), {"mid": s.mid})
            count = result.scalar()
            if count > 0:
                conn.execute(text(
                    """
                    UPDATE search_info SET update_stamp=:update_stamp, hits=:hits, state=:state, remarks=:remarks, score=:score, release_stamp=:release_stamp WHERE mid=:mid
                    """), s.dict())
            else:
                conn.execute(text(
                    """
                    INSERT INTO search_info (mid, cid, pid, name, sub_title, c_name, class_tag, area, language, year, initial, score, update_stamp, hits, state, remarks, release_stamp)
                    VALUES (:mid, :cid, :pid, :name, :sub_title, :c_name, :class_tag, :area, :language, :year, :initial, :score, :update_stamp, :hits, :state, :remarks, :release_stamp)
                    """), s.dict())
            save_search_tag(s)

# 判断是否存在search表
def exist_search_table(db_engine):
    with db_engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES LIKE 'search_info'"))
        return result.first() is not None

# 判断是否存在影片检索信息
def exist_search_info(db_engine, mid: int):
    with db_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM search_info WHERE mid=:mid"), {"mid": mid})
        return result.scalar() > 0

# 截断search_info表
def truncate_search_table(db_engine):
    with db_engine.connect() as conn:
        conn.execute(text('TRUNCATE TABLE search_info'))
        conn.commit()

# 影片检索相关的其他函数
def get_search_infos_by_tags(st: dict, page: Page) -> Optional[List[SearchInfo]]:
    """
    根据标签条件筛选影片信息
    :param st: 搜索标签参数字典
    :param page: 分页参数
    :return: 符合条件的SearchInfo列表
    """
    try:
        session = get_db()
        query = select(SearchInfo)
        
        # 处理各标签条件
        if st.get('pid'):
            query = query.where(SearchInfo.pid == st['pid'])
        if st.get('cid'):
            query = query.where(SearchInfo.cid == st['cid'])
        if st.get('year'):
            query = query.where(SearchInfo.year == st['year'])
            
        # 处理特殊标签条件
        if st.get('area') == '其它':
            tags = get_tags_by_title(st['pid'], 'Area')
            exclude_areas = [t.split(':')[1] for t in tags]
            query = query.where(SearchInfo.area.not_in(exclude_areas))
        elif st.get('area'):
            query = query.where(SearchInfo.area == st['area'])
            
        if st.get('language') == '其它':
            tags = get_tags_by_title(st['pid'], 'Language')
            exclude_langs = [t.split(':')[1] for t in tags]
            query = query.where(SearchInfo.language.not_in(exclude_langs))
        elif st.get('language'):
            query = query.where(SearchInfo.language == st['language'])
            
        if st.get('plot') == '其它':
            tags = get_tags_by_title(st['pid'], 'Plot')
            exclude_plots = [t.split(':')[1] for t in tags]
            for plot in exclude_plots:
                query = query.where(SearchInfo.class_tag.not_like(f'%{plot}%'))
        elif st.get('plot'):
            query = query.where(SearchInfo.class_tag.like(f'%{st["plot"]}%'))
            
        # 处理排序
        if st.get('sort') == 'release_stamp':
            query = query.order_by(SearchInfo.year.desc(), SearchInfo.release_stamp.desc())
        elif st.get('sort'):
            query = query.order_by(getattr(SearchInfo, st['sort']).desc())
            
        # 添加分页
        query = query.offset((page.current - 1) * page.page_size).limit(page.page_size)
        
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
    redis = redis_client or init_redis_conn()
    result = {}
    
    # 获取标题信息
    key = SEARCH_TITLE.format(pid)
    titles = redis.hgetall(key)
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
    redis = redis_client or init_redis_conn()
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
        tag_key = SEARCH_TAG.format(pid, t)
        if t == "Plot":
            tags = redis.zrevrange(tag_key, 0, 10)
        elif t == "Area":
            tags = redis.zrevrange(tag_key, 0, 11)
        elif t == "Language":
            tags = redis.zrevrange(tag_key, 0, 6)
        else:
            tags = redis.zrevrange(tag_key, 0, -1)
    return tags


def get_movie_list_by_pid(pid: int, page: Page) -> Optional[List[MovieBasicInfo]]:
    """
    通过Pid分类ID获取对应影片的数据信息
    :param pid: 分类ID
    :param page: 分页参数
    :return: 影片基本信息列表
    """
    try:
        session = get_db()
        # 计算总数
        count = session.exec(select(func.count()).select_from(SearchInfo).where(SearchInfo.pid == pid)).one()
        page.total = count
        page.page_count = (page.total + page.page_size - 1) // page.page_size
        
        # 查询数据
        query = select(SearchInfo).where(SearchInfo.pid == pid).order_by(SearchInfo.update_stamp.desc())\
            .offset((page.current - 1) * page.page_size).limit(page.page_size)
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
        session = get_db()
        # 计算总数
        count = session.exec(select(func.count()).select_from(SearchInfo).where(SearchInfo.cid == cid)).one()
        page.total = count
        page.page_count = (page.total + page.page_size - 1) // page.page_size
        
        # 查询数据
        query = select(SearchInfo).where(SearchInfo.cid == cid).order_by(SearchInfo.update_stamp.desc())\
            .offset((page.current - 1) * page.page_size).limit(page.page_size)
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
        session = get_db()
        # 当前时间偏移一个月
        t = datetime.now() - timedelta(days=30)
        
        query = select(SearchInfo).where(
            SearchInfo.pid == pid,
            SearchInfo.update_stamp > t.timestamp()
        ).order_by(SearchInfo.year.desc(), SearchInfo.hits.desc())\
            .offset((page.current - 1) * page.page_size).limit(page.page_size)
        
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
        session = get_db()
        # 当前时间偏移一个月
        t = datetime.now() - timedelta(days=30)
        
        query = select(SearchInfo).where(
            SearchInfo.cid == cid,
            SearchInfo.update_stamp > t.timestamp()
        ).order_by(SearchInfo.year.desc(), SearchInfo.hits.desc())\
            .offset((page.current - 1) * page.page_size).limit(page.page_size)
        
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
    query = query.offset((page.current - 1) * page.page_size).limit(page.page_size)
    
    try:
        session = get_db()
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
        redis = redis_client or init_redis_conn()
        if isinstance(data, (dict, list)):
            data = json.dumps(data, ensure_ascii=False)
        if expire > 0:
            redis.setex(key, expire, data)
        else:
            redis.set(key, data)
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
        redis = redis_client or init_redis_conn()
        data = redis.get(key)
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
        redis = redis_client or init_redis_conn()
        if isinstance(data, (dict, list)):
            data = json.dumps(data, ensure_ascii=False)
        if expire > 0:
            redis.setex(key, expire, data)
        else:
            redis.set(key, data)
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
        redis = redis_client or init_redis_conn()
        data = redis.get(key)
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
        redis = redis_client or init_redis_conn()
        return redis.delete(key) > 0
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
        redis = redis_client or init_redis_conn()
        data = redis.hget(MULTIPLE_SITE_DETAIL.format(site_id), key)
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
        session = get_db()
        # 处理影片名称，去除季、数字、剧场版等
        name = re.sub(r'(第.{1,3}季.*)|([0-9]{1,3})|(剧场版)|(\s\S*$)|(之.*)|([\p{P}\p{S}].*)', '', search.name)
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
        query = query.offset((page.current - 1) * page.page_size).limit(page.page_size)
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
        session = get_db()
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
        page.page_count = (page.total + page.page_size - 1) // page.page_size
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
            .offset((page.current - 1) * page.page_size)
            .limit(page.page_size)
        )
        search_list = session.exec(query).all()
        return search_list
    except Exception as e:
        print(f"查询失败: {e}")
        return None