from fastapi import APIRouter, Depends, HTTPException, Request
from logic.user_logic import UserLogic
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from model.system import response

userController = APIRouter()


class LoginRequest(BaseModel):
    userName: str
    password: str


@userController.post("/login")
async def user_login(req: LoginRequest):
    if not req.userName or not req.password:
        return response.failed("用户名和密码信息不能为空")
    token, err = UserLogic.user_login(req.userName, req.password)
    if err:
        return response.failed(err)
    # Go 端是通过 Header 返回新 token，这里也加上
    from fastapi import Response
    resp = response.success_only_msg("登录成功!!!")
    resp = Response(content=resp.body, status_code=200, media_type="application/json")
    resp.headers["new-token"] = token
    return resp


@userController.get("/user/info")
async def user_info():
    # 模拟从token中获取用户ID
    user_id = 1  # 这里需要根据实际情况从token中解析出用户ID
    # 获取用户信息
    user_info = UserLogic.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return response.success(user_info, "成功获取用户信息")
