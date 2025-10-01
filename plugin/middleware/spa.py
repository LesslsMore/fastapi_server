import mimetypes
import os

from fastapi import Request
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

# 确定静态文件目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")


# 2. 自定义中间件，用于路由静态资源
class SpaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # 2.1 API请求，直接放行给FastAPI处理
        if path.startswith("/api/"):
            return await call_next(request)

        if path.startswith("/proxy/"):
            return await call_next(request)

        # 2.2 定义Vue项目的路由前缀和对应的静态文件目录
        spa_roots = {
            "/danmu": os.path.join(STATIC_DIR, "danmu"),
            "/": os.path.join(STATIC_DIR, "dist"),
        }

        # 2.3 检查请求路径是否匹配某个Vue项目
        for prefix, root_dir in spa_roots.items():
            if path.startswith(prefix):
                # 构造可能存在的物理文件路径
                # e.g. /project1/assets/index.css -> /path/to/static/project1/assets/index.css
                relative_path = path[len(prefix):].lstrip('/')
                file_path = os.path.join(root_dir, relative_path)

                # 检查物理文件是否存在，并且不是目录
                if os.path.isfile(file_path):
                    # 如果是存在的静态文件（js, css, etc.），直接返回文件内容
                    mimetype, _ = mimetypes.guess_type(file_path)
                    return FileResponse(file_path, media_type=mimetype)
                else:
                    # 如果是SPA的深层链接（文件不存在），返回该项目的入口index.html
                    index_path = os.path.join(root_dir, "index.html")
                    if os.path.exists(index_path):
                        return FileResponse(index_path)

        # 2.4 如果没有任何匹配，可以继续执行后续中间件或FastAPI的默认行为 (例如返回404)
        return await call_next(request)
