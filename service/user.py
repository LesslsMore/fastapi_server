from typing import Optional

from fastapi import HTTPException

from model.system.user import User
from model.system.user import users_dao
from plugin.common.util.string_util import password_encrypt
from plugin.middleware.jwt_token import gen_token, save_user_token


class UserService:
    @staticmethod
    def get_user_info(id: int) -> dict:
        # 通过用户ID查询对应的用户信息
        user = users_dao.query_item(filter_dict={"id": id})
        if user:
            # 去除user信息中的不必要信息
            user_info = {
                "id": user.id,
                "user_name": user.user_name,
                "email": user.email,
                "gender": user.gender,
                "nick_name": user.nick_name,
                "avatar": user.avatar,
                "status": user.status
            }
            return user_info
        else:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    def user_login(account: str, password: str):
        """
        用户登录，账号可以为用户名或邮箱
        :param account: 用户名或邮箱
        :param password: 密码
        :return: (token, err)
        """
        user = UserService.get_user_by_name_or_email(account)
        if user is None:
            return None, "用户信息不存在!"
        if password_encrypt(password, user.salt) != user.password:
            return None, "用户名或密码错误"
        token = gen_token(user.id, user.user_name)
        save_user_token(token, user.id)
        return token, None

    @staticmethod
    # 初始化管理员账户
    def init_admin_account():
        user = users_dao.query_item({"user_name": "admin"})
        if user:
            return
        u = User(
            user_name="admin",
            password="admin",
            salt='4600d290531a589b',
            email="administrator@gmail.com",
            gender=2,
            nick_name="Zero",
            avatar="empty",
            status=0
        )
        u.password = password_encrypt(u.password, u.salt)

        users_dao.create_item(u)

    # 根据用户名或邮箱获取用户信息
    @staticmethod
    def get_user_by_name_or_email(user_name: str) -> Optional[User]:
        # 先通过用户名查找
        user = users_dao.query_item({"user_name": user_name})
        if user:
            return user

        # 如果没找到，再通过邮箱查找
        user = users_dao.query_item({"email": user_name})
        return user

    # 更新用户信息
    @staticmethod
    def update_user_info(u: User):
        users_dao.update_item(
            filter_dict={"id": u.id},
            update_dict={
                "password": u.password,
                "email": u.email,
                "nick_name": u.nick_name,
                "status": u.status
            }
        )
