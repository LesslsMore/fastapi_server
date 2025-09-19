from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from config.database import sync_engine
from dao.system.user_dao import init_admin_account
from plugin.init.spider_init import film_source_init
from plugin.init.web_init import basic_config_init, banners_init
from utils.get_scheduler import SchedulerUtil


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(sync_engine)

    init_admin_account()

    film_source_init()
    basic_config_init()
    banners_init()
    await SchedulerUtil.init_system_scheduler()
    yield
    await SchedulerUtil.close_system_scheduler()
    # Clean up the ML models and release the resources


def app_config(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有域名
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有HTTP方法
        allow_headers=["*"],  # 允许所有请求头
    )
    # app.add_middleware(AuthTokenMiddleware)
