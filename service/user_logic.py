from dao.system.user_dao import get_user_by_id, get_user_by_name_or_email
from plugin.common.util.string_util import password_encrypt
from plugin.middleware.jwt_token import gen_token, save_user_token


class UserLogic:
    @staticmethod
    def get_user_info(id: int) -> dict:
        # 通过用户ID查询对应的用户信息
        user = get_user_by_id(id)
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
        return {}

    @staticmethod
    def user_login(account: str, password: str):
        """
        用户登录，账号可以为用户名或邮箱
        :param account: 用户名或邮箱
        :param password: 密码
        :return: (token, err)
        """
        user = get_user_by_name_or_email(account)
        if user is None:
            return None, "用户信息不存在!"
        if password_encrypt(password, user.salt) != user.password:
            return None, "用户名或密码错误"
        token = gen_token(user.id, user.user_name)
        save_user_token(token, user.id)
        return token, None
