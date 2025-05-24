from model.service.film_detail import batch_save_original_detail, convert_film_details
from model.service.film_list import save_film_class
from model.system.collect_source import FilmSource
from model.system.movies import MovieDetail, MovieDescriptor, MovieUrlInfo
from typing import List

import json
from typing import List, Optional
from model.system.film_detail import FilmDetail
from plugin.common.conver.collect import gen_category_tree
from plugin.db.redis_client import redis_client, init_redis_conn
from plugin.db.postgres import get_db
import requests
from typing import Dict, Any, Optional

def api_get(uri: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Optional[bytes]:
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
        return None

def get_film_detail(uri: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10):
    # 设置分页请求参数
    params = params.copy()
    params['ac'] = 'detail'
    resp_bytes = api_get(uri, params, headers, timeout)
    if not resp_bytes:
        return [], '请求失败或无响应'
    try:
        import json
        detail_page = json.loads(resp_bytes)
        # detail_page 应包含 'list' 字段，对应 FilmDetailLPage 结构
        detail_list = detail_page.get('list', [])
        # 保存原始详情到 redis
        batch_save_original_detail([FilmDetail(**item) for item in detail_list])
        # 转换为业务 MovieDetail
        movie_list = convert_film_details([FilmDetail(**item) for item in detail_list])
        return movie_list, None
    except Exception as e:
        return [], f'解析失败: {e}'


def get_page_count(uri: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> int:
    """
    获取分页总页数，对应Go GetPageCount。
    """
    params = params.copy()
    if not params.get('ac'):
        params['ac'] = 'detail'
    params['pg'] = '1'
    resp_bytes = api_get(uri, params, headers, timeout)
    if not resp_bytes:
        raise Exception('response is empty')
    try:
        res = json.loads(resp_bytes)
        return int(res.get('pagecount', 0) or res.get('pageCount', 0) or 0)
    except Exception as e:
        raise Exception(f'解析分页数失败: {e}')


def get_category_tree(fs: FilmSource, params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
    """
    获取影视分类树，对应Go GetCategoryTree。
    """
    params = params.copy() if params else {}
    params['ac'] = 'list'
    params['pg'] = '1'
    resp_bytes = api_get(fs.uri, params, headers, timeout)
    if not resp_bytes:
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
        raise Exception(f'解析分类树失败: {e}')


def custom_search(uri: str, wd: str, params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
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
        return [FilmDetail(**item) for item in detail_list]
    except Exception:
        return []


def get_single_film(uri: str, ids: str, params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
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
        return FilmDetail(**detail_list[0]) if detail_list else None
    except Exception:
        return None


def failure_record(info: Dict[str, Any]):
    """
    记录采集失败信息。
    """
    # 可扩展为写入redis或数据库
    print(f"FailureRecord: {info}")


def film_detail_retry(uri: str, params: Dict[str, Any], retry: int = 1, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
    """
    影片详情重试机制。
    """
    for i in range(retry):
        movie_list, err = get_film_detail(uri, params, headers, timeout)
        if not err:
            return movie_list
    return []

class ResultModel:
    JsonResult = 0
    XmlResult = 1





# 站点类型常量
MASTER_COLLECT = 1
SLAVE_COLLECT = 2
COLLECT_VIDEO = 1

def collect_api_test(fs: FilmSource) -> None:
    """
    测试采集接口是否可用，参考Go版CollectApiTest实现。
    :param s: FilmSource对象或dict，需包含uri、collect_type、result_model等字段
    :raises Exception: 若接口不可用或数据格式不符则抛出异常
    """
    uri = fs.uri
    collect_type = fs.collectType
    result_model = fs.resultModel
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
    if result_model == ResultModel.JsonResult or str(result_model) == '0':
        try:
            json.loads(content)
        except Exception as e:
            raise Exception(f"测试失败, 返回数据异常, JSON序列化失败: {e}")
    elif result_model == ResultModel.XmlResult or str(result_model) == '1':
        try:
            ET.fromstring(content)
        except Exception as e:
            raise Exception(f"测试失败, 返回数据异常, XML序列化失败: {e}")
    else:
        raise Exception("测试失败, 接口返回值类型不符合规范")