from typing import Optional

from model.system.user import User, users_dao
from plugin.common.util.string_util import password_encrypt


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
def get_user_by_name_or_email(user_name: str) -> Optional[User]:
    # 先通过用户名查找
    user = users_dao.query_item({"user_name": user_name})
    if user:
        return user

    # 如果没找到，再通过邮箱查找
    user = users_dao.query_item({"email": user_name})
    return user


# 更新用户信息
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
