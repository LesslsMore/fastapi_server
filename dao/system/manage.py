import logging
from typing import List

from config import data_config
from dao.collect.kv_dao import KVDao
from model.system.manage import BasicConfig, Banner


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
                logging.info(f"GetSiteBasic Err: {e}")
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
                logging.info(f"GetBanners Error: {e}")
        return banners

    @staticmethod
    def save_banners(banners: List[Banner]):
        banners_list = [b.model_dump() for b in banners]
        return KVDao.set_value(data_config.BANNERS_KEY, banners_list)
