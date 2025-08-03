import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, openapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse, Response
from starlette.staticfiles import StaticFiles

from anime.anime_controller import anime_controller
from controller.CronController import CronController
from controller.collect_controller import collectController
from controller.film_controller import filmController
from controller.index_controller import indexController
from controller.manage_controller import manageController
from controller.spider_controller import spiderController
from controller.user_controller import userController
from exceptions.handle import handle_exception
from model.collect.MacType import MacType
from plugin.db import close_redis
from plugin.init.db_init import table_init
from plugin.init.spider_init import film_source_init
from plugin.init.web_init import basic_config_init, banners_init
from utils.get_scheduler import SchedulerUtil


@asynccontextmanager
async def lifespan(app: FastAPI):
    table_init()

    film_source_init()
    basic_config_init()
    banners_init()
    await SchedulerUtil.init_system_scheduler()
    yield
    await SchedulerUtil.close_system_scheduler()
    # Clean up the ML models and release the resources
    close_redis()


app = FastAPI(lifespan=lifespan)
# 加载全局异常处理方法
handle_exception(app)


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.api_route("/proxy/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(full_path: str, request: Request):
    # 从环境变量读取敏感信息（需提前配置）
    DANMU_APP_ID = os.getenv("danmu_appId")
    DANMU_APP_SECRET = os.getenv("danmu_appSecret")
    TARGET_SERVER = "https://api.dandanplay.net"

    # 构造目标 URL
    url = f"{TARGET_SERVER}/{full_path}"
    logging.info("Proxying request to:", url)

    # 读取请求体和请求头
    body = await request.body()
    headers = dict(request.headers)
    headers["X-AppId"] = DANMU_APP_ID
    headers["X-AppSecret"] = DANMU_APP_SECRET
    headers.pop("host", None)  # 避免 Host 被错误传递

    # 创建异步客户端请求
    async with httpx.AsyncClient() as client:
        try:
            proxy_response = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
                params=dict(request.query_params),
                timeout=30.0,
            )
            # 返回响应
            return Response(
                content=proxy_response.content,
                status_code=proxy_response.status_code,
                headers=dict(proxy_response.headers),
            )
        except httpx.RequestError as exc:
            return Response(content=f"Error: {str(exc)}", status_code=500)


# 捕获 404 异常并返回前端入口文件
@app.exception_handler(404)
async def spa_fallback(request: Request, exc: HTTPException):
    return FileResponse("dist/index.html")

app.include_router(prefix='/api', router=anime_controller)

app.include_router(prefix='/api', router=indexController)
app.include_router(prefix='/api', router=userController)
manageController.include_router(collectController)
manageController.include_router(CronController)
manageController.include_router(spiderController)
manageController.include_router(userController)
manageController.include_router(filmController)
app.include_router(prefix='/api', router=manageController)
# app.add_middleware(AuthTokenMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

app.mount("/", StaticFiles(directory="dist", html=True), name="dist")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logging_config = "logging.ini"  # 假设你把上面的配置保存为 logging.ini
    uvicorn.run(app, host="0.0.0.0", port=port, log_config=logging_config)
