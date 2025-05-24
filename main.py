from fastapi import FastAPI
import uvicorn

from config import config, load_dotenv
from plugin.db.postgres import init_postgres
from plugin.db.redis_client import init_redis_conn
from plugin.db.mysql import init_mysql
from fastapi.middleware.cors import CORSMiddleware
import os

from plugin.init.db_init import table_init
from plugin.init.spider_init import film_source_init
from plugin.init.web_init import basic_config_init, banners_init

app = FastAPI()


@app.get("/ping")
def ping():
    return {"message": "pong"}


from controller import index_controller, manage_controller

app.include_router(index_controller.router)
app.include_router(manage_controller.router)


@app.on_event("startup")
def startup_event():

    # init_mysql()
    init_postgres()
    init_redis_conn()
    film_source_init()
    table_init()
    basic_config_init()
    banners_init()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

if __name__ == "__main__":
    load_dotenv('config/.env.win')
    port = os.environ.get("PORT")
    # port = config['port']
    uvicorn.run(app, host="0.0.0.0", port=int(port))
