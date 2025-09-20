import logging

import httpx
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse, Response

from config.env import DanmuConfig


def app_handler(app: FastAPI):
    global ping

    @app.get("/ping")
    def ping():
        return {"message": "pong"}

    @app.api_route("/proxy/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def proxy(full_path: str, request: Request):
        # 从环境变量读取敏感信息（需提前配置）

        # 构造目标 URL
        url = f"{DanmuConfig.TARGET_SERVER}/{full_path}"
        logging.info("Proxying request to:", url)

        # 读取请求体和请求头
        body = await request.body()
        headers = dict(request.headers)
        headers["X-AppId"] = DanmuConfig.DANMU_APP_ID
        headers["X-AppSecret"] = DanmuConfig.DANMU_APP_SECRET
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
        return FileResponse("static/dist/index.html")

        # return FileResponse("static/danmu/index.html")
