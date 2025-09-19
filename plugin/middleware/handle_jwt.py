from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED

from plugin.middleware.jwt_token import parse_token, get_user_token_by_id, gen_token, save_user_token


class AuthTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_token = request.headers.get("auth-token")
        if not auth_token:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                                content={"code": 200, "msg": "用户未授权,请先登录", "data": None})
        uc, err = parse_token(auth_token)
        if uc is None:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                                content={"code": 200, "msg": "身份验证信息异常,请重新登录!!!", "data": None})
        t = await get_user_token_by_id(uc.user_id)
        if not t:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                                content={"code": 200, "msg": "身份验证信息已失效,请重新登录!!!", "data": None})
        if t != auth_token:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                                content={"code": 200, "msg": "账号在其它设备登录,身份验证信息失效,请重新登录!!!",
                                         "data": None})
        elif err is not None and getattr(err, 'expired', False):
            # token 过期但 redis 中 token 一致，自动刷新
            new_token = gen_token(uc.user_id, uc.userName)
            await save_user_token(new_token, uc.user_id)
            uc, _ = parse_token(new_token)
            response = await call_next(request)
            response.headers["new-token"] = new_token
            request.state.user_claims = uc
            return response
        request.state.user_claims = uc
        response = await call_next(request)
        return response


# 用法示例（在 FastAPI app 中添加中间件）
# from fastapi import FastAPI
# from plugin.middleware.handle_jwt import AuthTokenMiddleware
# app = FastAPI()
# app.add_middleware(AuthTokenMiddleware)


def AuthToken(request: Request):
    auth_token = request.headers.get("auth-token")
    if not auth_token:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                            content={"code": 200, "msg": "用户未授权,请先登录", "data": None})
    uc, err = parse_token(auth_token)
    if uc is None:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                            content={"code": 200, "msg": "身份验证信息异常,请重新登录!!!", "data": None})
    t = get_user_token_by_id(uc.user_id)
    if not t:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                            content={"code": 200, "msg": "身份验证信息已失效,请重新登录!!!", "data": None})
    if t != auth_token:
        return JSONResponse(status_code=HTTP_401_UNAUTHORIZED,
                            content={"code": 200, "msg": "账号在其它设备登录,身份验证信息失效,请重新登录!!!",
                                     "data": None})
    elif err is not None and getattr(err, 'expired', False):
        # token 过期但 redis 中 token 一致，自动刷新
        new_token = gen_token(uc.user_id, uc.userName)
        save_user_token(new_token, uc.user_id)
        uc, _ = parse_token(new_token)
        # response = await call_next(request)
        # response.headers["new-token"] = new_token
        request.state.user_claims = uc
    #     return response
    # request.state.user_claims = uc
