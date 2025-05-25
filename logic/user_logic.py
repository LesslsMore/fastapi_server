from service.system.user_service import get_user_by_id


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