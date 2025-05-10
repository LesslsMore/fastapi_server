from fastapi import FastAPI
import uvicorn

from config import config
from plugin.db.redis_client import init_redis_conn
from plugin.db.mysql import init_mysql
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "pong"}

from controller import index_controller, manage_controller

app.include_router(index_controller.router)
app.include_router(manage_controller.router)

@app.on_event("startup")
def startup_event():
    init_mysql()
    init_redis_conn()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

if __name__ == "__main__": 
	uvicorn.run(app, host="0.0.0.0", port=config['port'])