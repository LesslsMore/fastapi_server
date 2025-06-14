import logging
from sqlmodel import not_
import json

from dao.collect.MacVodDao import MacVodDao, mac_vod_to_movie_detail, mac_vod_list_to_movie_detail_list
from model.collect.MacVod import MacVod
from model.system.virtual_object import SearchVo
from plugin.db import redis_client, pg_engine
from sqlalchemy import text, update
from config.data_config import SEARCH_INFO_TEMP
from datetime import datetime, timedelta
from model.system.movies import MovieBasicInfo, MovieDetail
from model.system.search import SearchInfo

from typing import List, Optional
from sqlmodel import Session, select, func, or_
from plugin.db import get_session
from model.system.response import Page
from dao.collect.movie_dao import MovieDao, movie_detail_to_movie_basic_info
from dao.system.search_tag import batch_handle_search_tag, get_tags_by_title


def get_basic_info_by_search_info_list(search_info_list: List[SearchInfo]) -> List[MovieBasicInfo]:
    mids = [search_info.mid for search_info in search_info_list]
    mac_vod_list = MacVodDao.select_mac_vod_list(mids)

    movie_basic_info_list = []
    for mac_vod in mac_vod_list:
        movie_detail = mac_vod_to_movie_detail(mac_vod)
        movie_basic_info = movie_detail_to_movie_basic_info(movie_detail)
        movie_basic_info_list.append(movie_basic_info)
    return movie_basic_info_list


# 重置Search表
def reset_search_table():
    session = get_session()
    session.execute(text('DROP TABLE IF EXISTS search_info'))
    session.commit()


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

        # 返回分页参数
        GetPage(query, page)
        # 添加分页
        query = query.offset((page.current - 1) * page.pageSize).limit(page.pageSize)

        search_infos = session.exec(query).all()
        return search_infos
    except Exception as e:
        print(f"查询失败: {e}")
        return None


def GetPage(query, page: Page):
    count_query = select(func.count()).select_from(query.subquery())  # 计数查询

    # 执行获取数量
    with Session(pg_engine) as session:
        total = session.exec(count_query).one_or_none()
        if total:
            page.total = int(total)
        else:
            page.total = 0
        page.pageCount = int((page.total + page.pageSize - 1) / page.pageSize)


def GetSearchPage(s: SearchVo) -> List[SearchInfo]:
    with Session(pg_engine) as session:
        # 构建基础查询
        query = select(SearchInfo)

        # 添加动态查询条件
        if s.name:
            query = query.where(SearchInfo.name.like(f"%{s.name}%"))

        if s.cid and s.cid > 0:
            query = query.where(SearchInfo.cid == s.cid)
        elif s.pid and s.pid > 0:
            query = query.where(SearchInfo.pid == s.pid)

        if s.plot:
            query = query.where(SearchInfo.class_tag.like(f"%{s.plot}%"))

        if s.area:
            query = query.where(SearchInfo.area == s.area)

        if s.language:
            query = query.where(SearchInfo.language == s.language)

        if s.year and s.year > (datetime.now().year - 12):
            query = query.where(SearchInfo.year == s.year)

        if s.remarks:
            if s.remarks == "完结":
                query = query.where(SearchInfo.remarks.in_(["完结", "HD"]))
            else:
                query = query.where(not_(SearchInfo.remarks.in_(["完结", "HD"])))

        if s.beginTime and s.beginTime > 0:
            query = query.where(SearchInfo.update_stamp >= s.beginTime)

        if s.endTime and s.endTime > 0:
            query = query.where(SearchInfo.update_stamp <= s.endTime)

        # 返回分页参数
        GetPage(query, s.paging)

        # pageSize: int = None
        # current: int = None
        # total: int = None
        # pageCount: int = None

        # 计算分页偏移量
        offset = (s.paging.current - 1) * s.paging.pageSize

        # 执行分页查询
        results = session.exec(
            query.limit(s.paging.pageSize).offset(offset)
        ).all()

        return results


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
        search_info_list = session.exec(query).all()

        return get_basic_info_by_search_info_list(search_info_list)
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
        search_info_list = session.exec(query).all()

        return get_basic_info_by_search_info_list(search_info_list)
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
        return get_basic_info_by_search_info_list(search_infos)
        # return get_basic_info_by_search_infos(search_infos)
    except Exception as e:
        print(f"查询失败: {e}")
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
        search_info_list = session.exec(query).all()
        return get_basic_info_by_search_info_list(search_info_list)
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


def search_info_to_mdb(model: int) -> None:
    count = redis_client.zcard(SEARCH_INFO_TEMP)
    if count <= 0:
        return

    list_ = redis_client.zpopmax(SEARCH_INFO_TEMP, count)
    if not list_:
        return

    search_info_list = []
    for member, score in list_:
        info = SearchInfo(**json.loads(member))
        search_info_list.append(info)

    if model == 0:
        batch_save(search_info_list)
    elif model == 1:
        batch_save_or_update(search_info_list)

    search_info_to_mdb(model)


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
    session.exec(text("CREATE UNIQUE INDEX idx_mid ON search (mid)"))
    session.exec(text("CREATE INDEX idx_time ON search (update_stamp DESC)"))
    session.exec(text("CREATE INDEX idx_hits ON search (hits DESC)"))
    session.exec(text("CREATE INDEX idx_score ON search (score DESC)"))
    session.exec(text("CREATE INDEX idx_release ON search (release_stamp DESC)"))
    session.exec(text("CREATE INDEX idx_year ON search (year DESC)"))


def get_search_info(id):
    # 通过ID获取影片搜索信息
    session = get_session()
    search_info = session.exec(
        select(SearchInfo).where(SearchInfo.mid == id)
    ).first()
    return search_info
