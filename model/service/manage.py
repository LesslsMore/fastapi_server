from typing import List
from json import dumps, loads
from plugin.db.redis_client import init_redis_conn, get_redis_client
from config import data_config
from model.system.manage import BasicConfig, Banner

def save_site_basic(config: BasicConfig):
    redis_client = get_redis_client() or init_redis_conn()
    data = config.model_dump_json()
    return redis_client.set(data_config.SITE_CONFIG_BASIC, data, ex=data_config.MANAGE_CONFIG_EXPIRED)

def get_site_basic() -> BasicConfig:
    redis_client = get_redis_client() or init_redis_conn()
    data = redis_client.get(data_config.SITE_CONFIG_BASIC)
    if data:
        try:
            return BasicConfig.parse_raw(data)
        except Exception as e:
            print(f"GetSiteBasic Err: {e}")
    return BasicConfig(siteName="", domain="", logo="", keyword="", describe="", state=False, hint="")

def save_banners(banners: List[Banner]):
    redis_client = get_redis_client() or init_redis_conn()
    banners_list = [b.dict() for b in banners]
    data = dumps(banners_list, ensure_ascii=False)
    return redis_client.set(data_config.BANNERS_KEY, data, ex=data_config.MANAGE_CONFIG_EXPIRED)

def get_banners() -> List[Banner]:
    redis_client = get_redis_client() or init_redis_conn()
    data = redis_client.get(data_config.BANNERS_KEY)
    banners = []
    if data:
        try:
            banners_data = loads(data)
            banners = [Banner.parse_obj(b) for b in banners_data]
            banners.sort(key=lambda x: x.sort)
        except Exception as e:
            print(f"GetBanners Error: {e}")
    return banners