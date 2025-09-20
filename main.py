import os

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.configer import lifespan, app_config
from app.handler import app_handler
from app.router import app_router
from exceptions.handle import handle_exception

app = FastAPI(lifespan=lifespan)

# 加载全局异常处理方法
handle_exception(app)

app_handler(app)

app_router(app)

app_config(app)

static = os.path.join(os.path.dirname(__file__), "static")

# app.mount("/danmu", StaticFiles(directory=os.path.join(static, "danmu")), name="danmu")
app.mount("/", StaticFiles(directory=os.path.join(static, "dist")), name="dist")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8888))
    logging_config = "logging.ini"  # 假设你把上面的配置保存为 logging.ini
    uvicorn.run(app, host="0.0.0.0", port=port, log_config=logging_config)
