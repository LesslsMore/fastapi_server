from contextlib import asynccontextmanager

from fastapi import FastAPI, openapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os

from controller.collect_controller import collectController
from controller.index_controller import indexController
from controller.manage_controller import manageController
from controller.spider_controller import spiderController
from controller.user_controller import userController
from plugin.db import close_redis
from plugin.init.db_init import table_init
from plugin.init.spider_init import film_source_init
from plugin.init.web_init import basic_config_init, banners_init


@asynccontextmanager
async def lifespan(app: FastAPI):
    film_source_init()
    table_init()
    basic_config_init()
    banners_init()
    yield
    # Clean up the ML models and release the resources
    close_redis()


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
def ping():
    return {"message": "pong"}


app.include_router(indexController)
app.include_router(manageController)
manageController.include_router(collectController)
manageController.include_router(spiderController)
manageController.include_router(userController)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

if __name__ == "__main__":
    port = os.environ.get("PORT")
    # port = config['port']
    uvicorn.run(app, host="0.0.0.0", port=int(port))
