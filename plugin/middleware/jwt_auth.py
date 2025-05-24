import jwt
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import aioredis
import os

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

async def get_redis():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_token = request.headers.get("auth-token")
        if not auth_token:
            return JSONResponse(status_code=401, content={"code":200, "msg":"用户未授权,请先登录", "data":None})
        try:
            payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = str(payload.get("user_id"))
            user_name = payload.get("user_name")
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"code":200, "msg":"身份验证信息已失效,请重新登录!!!", "data":None})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"code":200, "msg":"无效的Token,请重新登录!!!", "data":None})
        redis_conn = await get_redis()
        redis_token = await redis_conn.get(f"user_token:{user_id}")
        if not redis_token:
            return JSONResponse(status_code=401, content={"code":200, "msg":"身份验证信息已失效,请重新登录!!!", "data":None})
        if redis_token != auth_token:
            return JSONResponse(status_code=401, content={"code":200, "msg":"账号在其它设备登录,身份验证信息失效,请重新登录!!!", "data":None})
        request.state.user = {"user_id": user_id, "user_name": user_name}
        response = await call_next(request)
        return response

def create_jwt_token(user_id, user_name, expires_delta=None):
    from datetime import datetime, timedelta
    to_encode = {"user_id": user_id, "user_name": user_name}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def save_user_token(token, user_id):
    redis_conn = await get_redis()
    await redis_conn.set(f"user_token:{user_id}", token, ex=7200)