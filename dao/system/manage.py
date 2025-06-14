from typing import List
from json import dumps, loads
from plugin.db import redis_client
from config import data_config
from model.system.manage import BasicConfig, Banner
from dao.collect.kv_dao import KVDao


class ManageService:
    @staticmethod
    def save_site_basic(config: BasicConfig):
        data = config.model_dump()
        return KVDao.set_value(data_config.SITE_CONFIG_BASIC, data)

    @staticmethod
    def get_site_basic() -> BasicConfig:
        data = KVDao.get_value(data_config.SITE_CONFIG_BASIC)
        if data:
            try:
                return BasicConfig(**data)
            except Exception as e:
                print(f"GetSiteBasic Err: {e}")
        return BasicConfig(siteName="", domain="", logo="", keyword="", describe="", state=False, hint="")

    @staticmethod
    def get_banners() -> List[Banner]:
        data = KVDao.get_value(data_config.BANNERS_KEY)
        banners = []
        if data:
            try:
                banners = [Banner(**b) for b in data]
                banners.sort(key=lambda x: x.sort)
            except Exception as e:
                print(f"GetBanners Error: {e}")
        return banners

    @staticmethod
    def save_banners(banners: List[Banner]):
        banners_list = [b.model_dump() for b in banners]
        return KVDao.set_value(data_config.BANNERS_KEY, banners_list)


def save_site_basic(config: BasicConfig):
    data = config.model_dump_json()
    return redis_client.set(data_config.SITE_CONFIG_BASIC, data, ex=data_config.MANAGE_CONFIG_EXPIRED)


def get_site_basic() -> BasicConfig:
    data = redis_client.get(data_config.SITE_CONFIG_BASIC)
    if data:
        try:
            return BasicConfig.parse_raw(data)
        except Exception as e:
            print(f"GetSiteBasic Err: {e}")
    return BasicConfig(siteName="", domain="", logo="", keyword="", describe="", state=False, hint="")


def save_banners(banners: List[Banner]):
    banners_list = [b.dict() for b in banners]
    data = dumps(banners_list, ensure_ascii=False)
    return redis_client.set(data_config.BANNERS_KEY, data, ex=data_config.MANAGE_CONFIG_EXPIRED)


def get_banners() -> List[Banner]:
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
