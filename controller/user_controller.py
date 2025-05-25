from fastapi import APIRouter, Depends, HTTPException
from logic.user_logic import UserLogic
from fastapi.security import OAuth2PasswordBearer

from model.system import response

userController = APIRouter()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@userController.get("/user/info")
async def user_info():
    # 模拟从token中获取用户ID
    user_id = 1  # 这里需要根据实际情况从token中解析出用户ID
    
    # 获取用户信息
    user_info = UserLogic.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return response.success(user_info, "成功获取用户信息")