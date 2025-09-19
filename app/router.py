from fastapi import FastAPI

from anime.controller import router as anime_controller
from controller.banner import router as banner_controller
from controller.collect import router as collect_controller
from controller.config import router as config_controller
from controller.cron import router as cron_controller
from controller.detail import router as detail_controller
from controller.film import router as film_controller
from controller.index import router as index_controller
from controller.manage import router as manage_controller
from controller.record import router as record_controller
from controller.spider import router as spider_controller
from controller.user import router as user_controller


def app_router(app: FastAPI):
    app.include_router(prefix='/api', router=anime_controller)
    app.include_router(prefix='/api', router=index_controller)
    app.include_router(prefix='/api', router=detail_controller)
    app.include_router(prefix='/api', router=user_controller)
    # 系统相关
    manage_controller.include_router(config_controller)
    # 轮播相关
    manage_controller.include_router(banner_controller)
    manage_controller.include_router(user_controller)
    # 采集相关
    collect_controller.include_router(record_controller)
    manage_controller.include_router(collect_controller)
    # 定时任务相关
    manage_controller.include_router(cron_controller)
    # 数据采集
    manage_controller.include_router(spider_controller)
    # 影视管理
    manage_controller.include_router(film_controller)
    app.include_router(prefix='/api', router=manage_controller)
