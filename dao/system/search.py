from datetime import datetime, timedelta
from typing import List, Optional

from config.constant import IOrderEnum
from dao.base_dao import ConfigPageQueryModel, FilterModel, SortModel, PageModel
from model.collect.MacVod import mac_vod_dao
from model.system.movies import MovieBasicInfo
from model.system.response import Page, set_page
from model.system.search import SearchInfo
from model.system.virtual_object import SearchVo
from plugin.common.conver.mac_vod import mac_vod_list_to_movie_basic_info_list, mac_vod_list_to_search_info_list


def get_basic_info_by_search_info_list(search_info_list: List[SearchInfo]) -> List[MovieBasicInfo]:
    mids = [search_info.mid for search_info in search_info_list]

    mac_vod_list = mac_vod_dao.query_items_by_ids(mids)
    movie_basic_info_list = mac_vod_list_to_movie_basic_info_list(mac_vod_list)
    return movie_basic_info_list


def GetSearchPage(s: SearchVo) -> List[SearchInfo]:
    # 构建过滤条件
    filters = []

    # 添加动态查询条件
    if s.name:
        filters.append(FilterModel(field_name='vod_name', field_ops='like', field_value=s.name))

    if s.cid and s.cid > 0:
        filters.append(FilterModel(field_name='type_id', field_ops='==', field_value=s.cid))
    elif s.pid and s.pid > 0:
        filters.append(FilterModel(field_name='type_id_1', field_ops='==', field_value=s.pid))

    if s.plot:
        filters.append(FilterModel(field_name='vod_class', field_ops='like', field_value=s.plot))

    if s.area:
        filters.append(FilterModel(field_name='vod_area', field_ops='==', field_value=s.area))

    if s.language:
        filters.append(FilterModel(field_name='vod_lang', field_ops='==', field_value=s.language))

    if s.year and s.year > (datetime.now().year - 12):
        filters.append(FilterModel(field_name='vod_year', field_ops='==', field_value=s.year))

    if s.remarks:
        if s.remarks == "完结":
            filters.append(FilterModel(field_name='vod_remarks', field_ops='in', field_value=["完结", "HD"]))
        else:
            # 对于 not_in 操作，需要在 BaseDao 中添加相应支持
            filters.append(FilterModel(field_name='vod_remarks', field_ops='not_in', field_value=["完结", "HD"]))

    if s.beginTime and s.beginTime > 0:
        filters.append(FilterModel(field_name='vod_time', field_ops='>=', field_value=s.beginTime))

    if s.endTime and s.endTime > 0:
        filters.append(FilterModel(field_name='vod_time', field_ops='<=', field_value=s.endTime))

    # 构造排序条件（根据需要添加合适的排序）
    sorts = [SortModel(field='vod_time', order='desc')]

    # 构造分页参数
    page_model = PageModel(page_no=s.paging.current, page_size=s.paging.pageSize)

    # 调用 get_items 方法
    items, total = mac_vod_dao.get_items(page=page_model, sorts=sorts, filters=filters)

    # 更新分页信息
    s.paging.total = total
    s.paging.pageCount = (total + s.paging.pageSize - 1) // s.paging.pageSize

    search_info_list = mac_vod_list_to_search_info_list(items)
    return search_info_list


def get_movie_list_by_pid(pid: int, page: Page) -> Optional[List[MovieBasicInfo]]:
    """
    通过Pid分类ID获取对应影片的数据信息
    :param pid: 分类ID
    :param page: 分页参数
    :return: 影片基本信息列表
    """
    page_items = mac_vod_dao.page_items({'type_id_1': pid}, ['vod_time'], IOrderEnum.descendent,
                                        ConfigPageQueryModel(page_num=page.current, page_size=page.pageSize))

    set_page(page, page_items)

    mac_vod_list = page_items.rows

    movie_basic_info_list = mac_vod_list_to_movie_basic_info_list(mac_vod_list)
    return movie_basic_info_list


def get_movie_list_by_cid(cid: int, page: Page) -> Optional[List[MovieBasicInfo]]:
    """
    通过Cid查找对应的影片分页数据
    :param cid: 分类ID
    :param page: 分页参数
    :return: 影片基本信息列表
    """
    page_items = mac_vod_dao.page_items({'type_id': cid}, ['vod_time'], IOrderEnum.descendent,
                                        ConfigPageQueryModel(page_num=page.current, page_size=page.pageSize))
    set_page(page, page_items)
    mac_vod_list = page_items.rows

    movie_basic_info_list = mac_vod_list_to_movie_basic_info_list(mac_vod_list)
    return movie_basic_info_list


def get_hot_movie_by_pid(pid: int, page: Page) -> Optional[List[SearchInfo]]:
    """
    获取Pid指定类别的热门影片
    :param pid: 分类ID
    :param page: 分页参数
    :return: 搜索信息列表
    """

    # 当前时间偏移一个月
    t = datetime.now() - timedelta(days=30)

    # 构造过滤条件
    filters = [
        FilterModel(field_name="type_id_1", field_ops="==", field_value=pid),
        FilterModel(field_name="vod_time_add", field_ops=">", field_value=t.timestamp())
    ]

    # 构造排序条件
    sorts = [
        SortModel(field="vod_year", order="desc"),
        SortModel(field="vod_hits", order="desc")
    ]

    # 构造分页参数
    page_model = PageModel(page_no=page.current, page_size=page.pageSize)

    # 调用 get_items 方法
    items, total = mac_vod_dao.get_items(page=page_model, sorts=sorts, filters=filters)

    search_info_list = mac_vod_list_to_search_info_list(items)
    return search_info_list
