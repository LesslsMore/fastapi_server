from fastapi import APIRouter, HTTPException
from fastapi import Request
from pydantic import BaseModel, field_validator

from service.user_logic import UserLogic
from utils.response_util import ResponseUtil  # 假设 ResponseUtil 在此路径

router = APIRouter(tags=['用户'])


class LoginRequest(BaseModel):
    userName: str
    password: str

    @field_validator('userName')
    def username_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('用户名不能为空')
        return v.strip()

    @field_validator('password')
    def password_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('密码不能为空')
        return v.strip()


@router.post("/login")
async def user_login(req: LoginRequest):
    token, err = UserLogic.user_login(req.userName, req.password)
    if err:
        return ResponseUtil.error(msg=err)
    # Go 端是通过 Header 返回新 token，这里也加上
    return ResponseUtil.success(msg="登录成功!!!", headers={"new-token": token}, media_type="application/json")


@router.get("/user/info")
async def user_info(request: Request):
    # 模拟从token中获取用户ID
    user_id = 1  # 这里需要根据实际情况从token中解析出用户ID
    # 获取用户信息
    user_info = UserLogic.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseUtil.success(data=user_info, msg="成功获取用户信息")
