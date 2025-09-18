from fastapi import APIRouter, Depends, HTTPException, Request, Response
from service.user_logic import UserLogic
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from utils.response_util import ResponseUtil  # 假设 ResponseUtil 在此路径

userController = APIRouter( tags=['用户'])


class LoginRequest(BaseModel):
    userName: str
    password: str


@userController.post("/login")
async def user_login(req: LoginRequest):
    if not req.userName or not req.password:
        return ResponseUtil.error(msg="用户名和密码信息不能为空")
    token, err = UserLogic.user_login(req.userName, req.password)
    if err:
        return ResponseUtil.error(msg=err)
    # Go 端是通过 Header 返回新 token，这里也加上
    return ResponseUtil.success(msg="登录成功!!!", headers={"new-token": token}, media_type="application/json")


@userController.get("/user/info")
async def user_info():
    # 模拟从token中获取用户ID
    user_id = 1  # 这里需要根据实际情况从token中解析出用户ID
    # 获取用户信息
    user_info = UserLogic.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseUtil.success(data=user_info, msg="成功获取用户信息")