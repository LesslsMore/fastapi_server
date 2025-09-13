import logging
import re
from typing import List, Optional

from sqlmodel import func
from sqlmodel import or_, select

from dao.system.search import GetPage
from dao.system.search_tag import get_tags_by_title, handle_tag_str
from demo.sql import get_session
from model.collect.MacVod import MacVod
from model.system.movies import MovieBasicInfo, MovieDetail
from model.system.response import Page
from plugin.common.conver.mac_vod import mac_vod_list_to_movie_basic_info_list


def get_mac_vod_list_by_tags(st: dict, page: Page) -> Optional[List[MacVod]]:
    """
    根据标签条件筛选影片信息
    :param st: 搜索标签参数字典
    :param page: 分页参数
    :return: 符合条件的SearchInfo列表
    """
    try:
        with get_session() as session:
            query = select(MacVod)

            # 处理各标签条件
            if st.get('Pid'):
                query = query.where(MacVod.type_id_1 == st['Pid'])
            if st.get('Cid'):
                query = query.where(MacVod.type_id == st['Cid'])
            if st.get('Year'):
                query = query.where(MacVod.vod_year == st['Year'])

            # 处理特殊标签条件
            if st.get('Area') == '其它':
                tags = get_tags_by_title(st['Pid'], 'Area')
                exclude_areas = [t.split(':')[1] for t in tags]
                query = query.where(MacVod.vod_area.not_in(exclude_areas))
            elif st.get('Area'):
                query = query.where(MacVod.vod_area == st['Area'])

            if st.get('Language') == '其它':
                tags = get_tags_by_title(st['Pid'], 'Language')
                exclude_langs = [t.split(':')[1] for t in tags]
                query = query.where(MacVod.vod_lang.not_in(exclude_langs))
            elif st.get('Language'):
                query = query.where(MacVod.vod_lang == st['Language'])

            if st.get('Plot') == '其它':
                tags = get_tags_by_title(st['Pid'], 'Plot')
                exclude_plots = [t.split(':')[1] for t in tags]
                for plot in exclude_plots:
                    query = query.where(MacVod.vod_class.not_like(f'%{plot}%'))
            elif st.get('Plot'):
                query = query.where(MacVod.vod_class.like(f'%{st["Plot"]}%'))

            # 处理排序
            if st.get('Sort') == 'release_stamp':
                query = query.order_by(MacVod.vod_year.desc(), MacVod.vod_time_add.desc())
            elif st.get('Sort') == 'update_stamp':
                query = query.order_by(MacVod.vod_time.desc())
            elif st.get('Sort') == 'hits':
                query = query.order_by(MacVod.vod_hits.desc())
            elif st.get('Sort') == 'score':
                query = query.order_by(MacVod.vod_douban_score.desc())

            # 返回分页参数
            GetPage(query, page)
            # 添加分页
            query = query.offset((page.current - 1) * page.pageSize).limit(page.pageSize)

            mac_vod_list = session.exec(query).all()
            return mac_vod_list
    except Exception as e:
        logging.info(f"查询失败: {e}")
        return None


def search_mac_vod_keyword(keyword: str, page: Page) -> Optional[List[MacVod]]:
    """
    根据关键字对影片名称和副标题进行模糊查询，支持分页，返回符合条件的影片信息列表。
    :param keyword: 搜索关键字
    :param page: 分页参数
    :return: SearchInfo列表
    """
    try:
        with get_session() as session:
            # 统计满足条件的数据量
            count = session.exec(
                select(func.count()).select_from(MacVod)
                .where(
                    or_(
                        MacVod.vod_name.contains(keyword),
                        MacVod.vod_sub.contains(keyword)
                    )
                )
            ).one()
            page.total = count
            page.pageCount = (page.total + page.pageSize - 1) // page.pageSize
            # 查询满足条件的数据
            query = (
                select(MacVod)
                .where(
                    or_(
                        MacVod.vod_name.contains(keyword),
                        MacVod.vod_sub.contains(keyword)
                    )
                )
                .order_by(MacVod.vod_year.desc(), MacVod.vod_time_add.desc())
                .offset((page.current - 1) * page.pageSize)
                .limit(page.pageSize)
            )
            search_list = session.exec(query).all()
            return search_list
    except Exception as e:
        logging.info(f"查询失败: {e}")
        return None


def get_relate_mac_vod_basic_info(movie_detail: MovieDetail, page: Page) -> Optional[List[MovieBasicInfo]]:
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
    # cid = movie_detail.cid,
    # name = movie_detail.name,
    # class_tag = movie_detail.descriptor.classTag,
    # area = movie_detail.descriptor.area,
    # language = movie_detail.descriptor.language,

    try:
        with get_session() as session:
            # 确保分页参数 current 至少为 1
            page.current = max(1, page.current)
            # 处理影片名称，去除季、数字、剧场版等
            name = re.sub(r'(第.{1,3}季.*)|([0-9]{1,3})|(剧场版)|([\s\S]*$)|(之.*)|([^u4e00-u9fa5\w].*)', '',
                          movie_detail.name)
            # 如果处理后长度没变且大于10，做截断
            if len(name) == len(movie_detail.name) and len(name) > 10:
                name = name[:((len(name) // 5) * 3)]
            # 名称相似匹配
            query = select(MacVod).where(
                MacVod.type_id == movie_detail.cid,
                or_(MacVod.vod_name.contains(name), MacVod.vod_sub.contains(name))
            )
            # 排除自身mid
            if movie_detail.id:
                query = query.where(MacVod.vod_id != movie_detail.id)
            # 剧情标签模糊匹配
            class_tag = (movie_detail.descriptor.classTag or '').replace(' ', '')
            tag_conditions = []
            if ',' in class_tag:
                for t in class_tag.split(','):
                    tag_conditions.append(MacVod.vod_class.contains(t))
            elif '/' in class_tag:
                for t in class_tag.split('/'):
                    tag_conditions.append(MacVod.vod_class.contains(t))
            elif class_tag:
                tag_conditions.append(MacVod.vod_class.contains(class_tag))
            if tag_conditions:
                query = query.where(or_(*tag_conditions))
            # 分页
            query = query.offset((page.current - 1) * page.pageSize).limit(page.pageSize)
            mac_vod_list = session.exec(query).all()
            movie_basic_info_list = mac_vod_list_to_movie_basic_info_list(mac_vod_list)
            return movie_basic_info_list
    except Exception as e:
        logging.info(f"查询相关影片失败: {e}")
        return None


def get_mac_vod_list_by_sort(sort_type: int, pid: int, page: Page) -> Optional[List[MovieBasicInfo]]:
    """
    根据排序类型返回对应分类的影片基本信息
    :param sort_type: 排序类型 0-最新上映 1-热度排行 2-最近更新
    :param pid: 分类ID
    :param page: 分页参数
    :param session: 数据库会话(通过依赖注入获取)
    :return: 影片基本信息列表
    """
    query = select(MacVod).where(MacVod.type_id_1 == pid)

    # 根据排序类型添加排序条件
    if sort_type == 0:
        query = query.order_by(MacVod.vod_year.desc(), MacVod.vod_time_add.desc())
    elif sort_type == 1:
        query = query.order_by(MacVod.vod_hits.desc())
    elif sort_type == 2:
        query = query.order_by(MacVod.vod_time.desc())

    # 添加分页限制
    query = query.offset((page.current - 1) * page.pageSize).limit(page.pageSize)

    try:
        with get_session() as session:
            mac_vod_list = session.exec(query).all()

            movie_basic_info_list = mac_vod_list_to_movie_basic_info_list(mac_vod_list)
            return movie_basic_info_list
    except Exception as e:
        logging.info(f"查询失败: {e}")
        return None


def get_search_tag_by_stat(pid: int) -> dict:
    """
    通过影片分类Pid返回对应分类的tag信息
    :param pid: 分类ID
    :return: 包含标签信息的字典
    """
    result = {}

    # 获取标题信息
    titles = {
        "Category": "类型",
        "Plot": "剧情",
        "Area": "地区",
        "Language": "语言",
        "Year": "年份",
        "Initial": "首字母",
        "Sort": "排序"
    }

    result["titles"] = titles

    # 处理标签信息
    tag_map = {}
    for title in titles:
        tags = get_tags_by_title(pid, title)
        tag_map[title] = handle_tag_str(title, tags)

    result["tags"] = tag_map
    result["sortList"] = ["Category", "Plot", "Area", "Language", "Year", "Sort"]

    return result
