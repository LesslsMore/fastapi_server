from sqlalchemy import text
from sqlmodel import SQLModel, Field, Session
from typing import Optional

from model.system.user import User
from plugin.common.util.string_util import generate_salt, password_encrypt
from plugin.db import get_db, pg_engine
import logging
from sqlmodel import select

# 创建用户表
def create_user_table():
    session = get_db()
    if not exist_user_table():
        session.execute(
            '''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(255),
            password VARCHAR(255),
            salt VARCHAR(255),
            email VARCHAR(255),
            gender INT,
            nick_name VARCHAR(255),
            avatar VARCHAR(255),
            status INT,
            reserve1 VARCHAR(255),
            reserve2 VARCHAR(255),
            reserve3 VARCHAR(255)
        )'''
        )
        session.commit()

# 判断用户表是否存在
def exist_user_table() -> bool:
    session = get_db()
    result = session.execute(text("SELECT to_regclass('users')")).fetchone()
    return result[0] is not None

# 初始化管理员账户
def init_admin_account():
    session = get_db()

    # user = get_user_by_name_or_email(session, "admin")
    user = None
    if user:
        return
    u = User(
        user_name="admin",
        password="admin",
        salt=generate_salt(),
        email="administrator@gmail.com",
        gender=2,
        nick_name="Zero",
        avatar="empty",
        status=0
    )
    u.password = password_encrypt(u.password, u.salt)
    session.add(u)
    session.commit()

# 根据用户名或邮箱获取用户信息
def get_user_by_name_or_email(user_name: str) -> Optional[User]:
    session = get_db()
    result = session.execute(text("SELECT * FROM users WHERE user_name = :user_name OR email = :user_name"), {"user_name": user_name}).fetchone()
    if result:
        return User(**result)
    return None

# 根据ID获取用户信息
def get_user_by_id(id: int) -> Optional[User]:
    session = get_db()
    statement = select(User).where(User.id == id)
    result = session.exec(statement).first()
    if result:
        return result
    return None

# 更新用户信息
def update_user_info(u: User):
    session = get_db()
    session.execute(text("UPDATE users SET password = :password, email = :email, nick_name = :nick_name, status = :status WHERE id = :id"), {
        "password": u.password,
        "email": u.email,
        "nick_name": u.nick_name,
        "status": u.status,
        "id": u.id
    })
    session.commit()