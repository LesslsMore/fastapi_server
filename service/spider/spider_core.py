import json
import logging
from typing import Dict, Any, Optional

import requests

from dao.collect.category import CategoryService
from model.collect.mac.vod import MacVod, mac_vod_dao
from model.collect.collect_source import FilmSource, CollectResultModel


def api_get(uri: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Optional[
    bytes]:
    try:
        # 设置随机 User-Agent，可扩展
        default_headers = {'User-Agent': 'Mozilla/5.0'}
        if headers:
            default_headers.update(headers)
        resp = requests.get(uri, params=params, headers=default_headers, timeout=timeout)
        if resp.status_code in [200] + list(range(300, 400)):
            return resp.json()
        return None
    except Exception as e:
        logging.error(f"API请求失败: {e}")
        return None


def get_film_detail(uri: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10):
    # 设置分页请求参数
    params = params.copy()
    params['ac'] = 'detail'
    logging.info(f"请求详情页: {uri}, 参数: {params}")
    resp = api_get(uri, params, headers, timeout)

    # detail_page 应包含 'list' 字段，对应 FilmDetailLPage 结构
    film_detail_list = resp.get('list', [])
    # 保存原始详情到 redis
    mac_vod_list = [MacVod(**item) for item in film_detail_list]
    mac_vod_dao.upsert_items(mac_vod_list)

    logging.info(f"保存原始详情成功: {len(mac_vod_list)}")
    # 转换为业务 MovieDetail
    # movie_detail_list = mac_vod_list_to_movie_detail_list([MacVod(**item) for item in film_detail_list])
    return mac_vod_list, None


def get_page_count(uri: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None,
                   timeout: int = 10) -> int:
    """
    获取分页总页数，对应Go GetPageCount。
    """
    params = params.copy()
    if not params.get('ac'):
        params['ac'] = 'detail'
    params['pg'] = '1'
    logging.info(f"请求分页数: {uri}, 参数: {params}")
    resp = api_get(uri, params, headers, timeout)
    page_count = int(resp.get('pagecount', 0) or resp.get('pageCount', 0) or 0)
    logging.info(f"获取分页数: {page_count}")
    return page_count


def get_category_tree(film_source: FilmSource, params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None,
                      timeout: int = 10):
    """
    获取影视分类树，对应Go GetCategoryTree。
    """
    params = params.copy() if params else {}
    params['ac'] = 'list'
    params['pg'] = '1'
    resp = api_get(film_source.uri, params, headers, timeout)

    class_list = resp.get('class', [])
    # 假设有 GenCategoryTree、SaveFilmClass 方法
    mac_type_list = CategoryService.save_mac_type(class_list)

    return mac_type_list


def collect_api_test(film_source: FilmSource) -> None:
    uri = film_source.uri
    collect_type = film_source.collectType
    result_model = film_source.resultModel
    # if not uri or not collect_type or not result_model:
    #     raise Exception("参数缺失，无法测试采集接口")
    params = {
        'ac': collect_type,
        'pg': '3'
    }
    try:
        resp = requests.get(uri, params=params, timeout=10)
        resp.raise_for_status()
        content = resp.content
    except Exception as e:
        raise Exception(f"测试失败, 请求响应异常: {e}")
    # 判断返回类型
    if result_model == CollectResultModel.JsonResult or str(result_model) == '0':
        try:
            json.loads(content)
        except Exception as e:
            raise Exception(f"测试失败, 返回数据异常, JSON序列化失败: {e}")
    elif result_model == CollectResultModel.XmlResult or str(result_model) == '1':
        try:
            ET.fromstring(content)
        except Exception as e:
            raise Exception(f"测试失败, 返回数据异常, XML序列化失败: {e}")
    else:
        raise Exception("测试失败, 接口返回值类型不符合规范")
