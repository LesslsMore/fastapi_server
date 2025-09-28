import os

import uvicorn
from dotenv import find_dotenv, load_dotenv

from plugin.middleware.spa import SpaMiddleware

env_file = '.env.dev'
# env_file = '.env.neon'
# env_file = '.env.render'
# 运行环境不为空时按命令行参数加载对应.env文件

# 加载配置
load_dotenv(find_dotenv(env_file))

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.configer import lifespan, app_config
from app.handler import app_handler
from app.router import app_router
from exceptions.handle import handle_exception

# app = FastAPI()

app_api = FastAPI(lifespan=lifespan)

static = os.path.join(os.path.dirname(__file__), "static")

# 加载全局异常处理方法
handle_exception(app_api)

app_handler(app_api)

app_router(app_api)

# app_handler_static(app_api)

app_config(app_api)

app_api.add_middleware(SpaMiddleware)

# app_cms = FastAPI()
# app_play = FastAPI()

# app_api.mount("/", StaticFiles(directory=os.path.join(static, "danmu")), name="danmu")


# app_api.mount("/", StaticFiles(directory=os.path.join(static, "dist")), name="dist")

# app.mount("/", app_api)
# # app.mount("/danmu", app_play)
# app.mount("/", app_cms)

app = app_api

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8888))
    logging_config = "logging.ini"  # 假设你把上面的配置保存为 logging.ini
    uvicorn.run(app, host="0.0.0.0", port=port, log_config=logging_config)
