from typing import List
from model.system.manage import BasicConfig, Banner
from model.service.manage import get_site_basic, save_site_basic, get_banners, save_banners

class ManageLogic:
    @staticmethod
    def get_site_basic_config() -> BasicConfig:
        return get_site_basic()

    @staticmethod
    def update_site_basic(config: BasicConfig):
        return save_site_basic(config)

    @staticmethod
    def get_banners() -> List[Banner]:
        return get_banners()

    @staticmethod
    def save_banners(banners: List[Banner]):
        return save_banners(banners)