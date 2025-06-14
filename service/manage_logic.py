from typing import List
from model.system.manage import BasicConfig, Banner
from dao.system.manage import get_site_basic, save_site_basic, get_banners, save_banners, ManageService


class ManageLogic:
    @staticmethod
    def get_site_basic_config() -> BasicConfig:
        return ManageService.get_site_basic()

    @staticmethod
    def update_site_basic(config: BasicConfig):
        return ManageService.save_site_basic(config)

    @staticmethod
    def get_banners() -> List[Banner]:
        return ManageService.get_banners()

    @staticmethod
    def save_banners(banners: List[Banner]):
        return ManageService.save_banners(banners)