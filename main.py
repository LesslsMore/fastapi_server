from fastapi import FastAPI
import uvicorn

from plugin.db.redis_client import init_redis_conn
from plugin.db.mysql import init_mysql

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

if __name__ == "__main__": 
	uvicorn.run(app, host="0.0.0.0", port=8000)