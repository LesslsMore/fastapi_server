import logging

from model.collect.MacType import MacType, mac_type_dao

from dao.collect.categories import CategoryTreeService
from dao.collect.MacVodDao import MacVodDao
from dao.collect.film_list import save_film_class
from model.collect.collect_source import FilmSource, CollectResultModel

import json
from model.collect.MacVod import MacVod
from plugin.common.conver.collect import gen_category_tree
import requests
from typing import Dict, Any, Optional, List


def api_get(uri: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Optional[
    bytes]:
    try:
        # 设置随机 User-Agent，可扩展
        default_headers = {'User-Agent': 'Mozilla/5.0'}
        if headers:
            default_headers.update(headers)
        resp = requests.get(uri, params=params, headers=default_headers, timeout=timeout)
        if resp.status_code in [200] + list(range(300, 400)) and resp.content:
            return resp.content
        return None
    except Exception as e:
        logging.error(f"API请求失败: {e}")
        return None


def get_film_detail(uri: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10):
    # 设置分页请求参数
    params = params.copy()
    params['ac'] = 'detail'
    logging.info(f"请求详情页: {uri}, 参数: {params}")
    resp_bytes = api_get(uri, params, headers, timeout)
    if not resp_bytes:
        return [], '请求失败或无响应'
    try:
        detail_page = json.loads(resp_bytes)
        # detail_page 应包含 'list' 字段，对应 FilmDetailLPage 结构
        film_detail_list = detail_page.get('list', [])
        # 保存原始详情到 redis
        mac_vod_list = [MacVod(**item) for item in film_detail_list]
        MacVodDao.batch_save_film_detail(mac_vod_list)
        logging.info(f"保存原始详情成功: {len(mac_vod_list)}")
        # 转换为业务 MovieDetail
        # movie_detail_list = mac_vod_list_to_movie_detail_list([MacVod(**item) for item in film_detail_list])
        return mac_vod_list, None
    except Exception as e:
        logging.error(f"解析详情失败: {e}")
        return [], f'解析失败: {e}'


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
    resp_bytes = api_get(uri, params, headers, timeout)
    if not resp_bytes:
        logging.error('response is empty')
        raise Exception('response is empty')
    try:
        res = json.loads(resp_bytes)
        page_count = int(res.get('pagecount', 0) or res.get('pageCount', 0) or 0)
        logging.info(f"获取分页数: {page_count}")
        return page_count
    except Exception as e:
        logging.error(f"解析分页数失败: {e}")
        raise Exception(f'解析分页数失败: {e}')


def get_category_tree(film_source: FilmSource, params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None,
                      timeout: int = 10):
    """
    获取影视分类树，对应Go GetCategoryTree。
    """
    params = params.copy() if params else {}
    params['ac'] = 'list'
    params['pg'] = '1'
    resp_bytes = api_get(film_source.uri, params, headers, timeout)
    if not resp_bytes:
        logging.error('filmListPage 数据获取异常 : Resp Is Empty')
        raise Exception('filmListPage 数据获取异常 : Resp Is Empty')
    try:
        film_list_page = json.loads(resp_bytes)
        cl = film_list_page.get('class', [])
        # 假设有 GenCategoryTree、SaveFilmClass 方法
        # from plugin.common.conver.Collect import gen_category_tree
        # from model.collect.film_list import save_film_class
        tree = gen_category_tree(cl)
        save_film_class(cl)
        return tree
    except Exception as e:
        logging.error(f"解析分类树失败: {e}")
        raise Exception(f'解析分类树失败: {e}')


def get_category_tree(film_source: FilmSource, params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None,
                      timeout: int = 10):
    """
    获取影视分类树，对应Go GetCategoryTree。
    """
    params = params.copy() if params else {}
    params['ac'] = 'list'
    params['pg'] = '1'
    resp_bytes = api_get(film_source.uri, params, headers, timeout)
    if not resp_bytes:
        logging.error('filmListPage 数据获取异常 : Resp Is Empty')
        raise Exception('filmListPage 数据获取异常 : Resp Is Empty')
    try:
        film_list_page = json.loads(resp_bytes)
        cl = film_list_page.get('class', [])
        # 假设有 GenCategoryTree、SaveFilmClass 方法
        # from plugin.common.conver.Collect import gen_category_tree
        # from model.collect.film_list import save_film_class
        tree = gen_category_tree(cl)
        save_film_class(cl)
        return tree
    except Exception as e:
        logging.error(f"解析分类树失败: {e}")
        raise Exception(f'解析分类树失败: {e}')


def get_category_tree_by_db():
    mac_type_list: List[MacType] = mac_type_dao.query_items({'type_status': 1})
    cl = [mac_type.model_dump() for mac_type in mac_type_list]
    category_tree = gen_category_tree(cl)
    save_film_class(cl)
    CategoryTreeService.save_category_tree(category_tree)


def custom_search(uri: str, wd: str, params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None,
                  timeout: int = 10):
    """
    自定义搜索，支持影片名模糊搜索。
    """
    params = params.copy() if params else {}
    params['ac'] = 'detail'
    params['pg'] = '1'
    params['wd'] = wd
    resp_bytes = api_get(uri, params, headers, timeout)
    if not resp_bytes:
        return []
    try:
        detail_page = json.loads(resp_bytes)
        detail_list = detail_page.get('list', [])
        return [MacVod(**item) for item in detail_list]
    except Exception:
        return []


def get_single_film(uri: str, ids: str, params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None,
                    timeout: int = 10):
    """
    获取单一影片信息。
    """
    params = params.copy() if params else {}
    params['ac'] = 'detail'
    params['pg'] = '1'
    params['ids'] = ids
    resp_bytes = api_get(uri, params, headers, timeout)
    if not resp_bytes:
        return None
    try:
        detail_page = json.loads(resp_bytes)
        detail_list = detail_page.get('list', [])
        return MacVod(**detail_list[0]) if detail_list else None
    except Exception:
        return None


def failure_record(info: Dict[str, Any]):
    """
    记录采集失败信息。
    """
    # 可扩展为写入redis或数据库
    logging.info(f"FailureRecord: {info}")


def film_detail_retry(uri: str, params: Dict[str, Any], retry: int = 1, headers: Optional[Dict[str, str]] = None,
                      timeout: int = 10):
    """
    影片详情重试机制。
    """
    for i in range(retry):
        movie_list, err = get_film_detail(uri, params, headers, timeout)
        if not err:
            return movie_list
    return []


def collect_api_test(film_source: FilmSource) -> None:
    """
    测试采集接口是否可用，参考Go版CollectApiTest实现。
    :param s: FilmSource对象或dict，需包含uri、collect_type、result_model等字段
    :raises Exception: 若接口不可用或数据格式不符则抛出异常
    """
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
