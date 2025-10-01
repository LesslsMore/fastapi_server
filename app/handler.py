import logging

import httpx
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse, Response

from config.env import DanmuConfig


def app_handler(app: FastAPI):
    @app.api_route("/proxy/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def proxy(full_path: str, request: Request):
        # 从环境变量读取敏感信息（需提前配置）

        # 构造目标 URL
        url = f"{DanmuConfig.TARGET_SERVER}/{full_path}"
        logging.info(f"Proxying request to: {url}")

        # 读取请求体和请求头
        body = await request.body()

        headers = dict(request.headers)
        # 添加这两行，明确要求不压缩
        headers["Accept-Encoding"] = "identity"  # 告诉服务器不要压缩
        headers.pop("accept-encoding", None)  # 移除可能的压缩头

        # 其他头部设置保持不变
        headers["X-AppId"] = DanmuConfig.DANMU_APP_ID
        headers["X-AppSecret"] = DanmuConfig.DANMU_APP_SECRET
        headers.pop("host", None)

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
        # @app.exception_handler(404)
        # async def spa_fallback(request: Request, exc: HTTPException):
        #     return FileResponse("static/dist/index.html")

        return FileResponse("static/danmu/index.html")

#     # 为每个SPA项目添加一个捕获所有请求的路由，返回其index.html
#     @app.api_route("/danmu/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
#     async def proxy(full_path: str, request: Request):
#         # 这里需要逻辑来确定rest_of_path属于哪个项目，然后返回对应的index.html
#         # 这种方法通常需要更多的路径解析逻辑，不如中间件方案清晰。
#         return FileResponse("static/danmu/index.html")
#
# def app_handler_static(app: FastAPI):
#     @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
#     async def proxy(full_path: str, request: Request):
#         # 这里需要逻辑来确定rest_of_path属于哪个项目，然后返回对应的index.html
#         # 这种方法通常需要更多的路径解析逻辑，不如中间件方案清晰。
#         return FileResponse("static/dist/index.html")
