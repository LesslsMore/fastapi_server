import jwt
import os
from datetime import datetime, timedelta
from config.security_config import PRIVATE_KEY, PUBLIC_KEY, AUTH_TOKEN_EXPIRES, USER_TOKEN_KEY, ISSUER
from plugin.db import redis_client

ALGORITHM = "RS256"


class UserClaims:
    def __init__(self, user_id, user_name, exp=None, iat=None, nbf=None, iss=None, sub=None, aud=None, jti=None):
        self.user_id = user_id
        self.user_name = user_name
        self.exp = exp
        self.iat = iat
        self.nbf = nbf
        self.iss = iss
        self.sub = sub
        self.aud = aud
        self.jti = jti

    def to_dict(self):
        d = {"user_id": self.user_id, "user_name": self.user_name}
        if self.exp: d["exp"] = self.exp
        if self.iat: d["iat"] = self.iat
        if self.nbf: d["nbf"] = self.nbf
        if self.iss: d["iss"] = self.iss
        if self.sub: d["sub"] = self.sub
        if self.aud: d["aud"] = self.aud
        if self.jti: d["jti"] = self.jti
        return d


# def load_private_key():
#     if os.path.exists(PRIVATE_KEY):
#         with open(PRIVATE_KEY, "rb") as f:
#             return f.read()
#     return PRIVATE_KEY.encode()
#
# def load_public_key():
#     if os.path.exists(PUBLIC_KEY):
#         with open(PUBLIC_KEY, "rb") as f:
#             return f.read()
#     return PUBLIC_KEY.encode()

def gen_token(user_id, user_name):
    now = datetime.utcnow()
    exp = now + timedelta(hours=AUTH_TOKEN_EXPIRES)
    claims = UserClaims(
        user_id=user_id,
        user_name=user_name,
        exp=exp,
        iat=now,
        nbf=now - timedelta(seconds=10),
        iss=ISSUER,
        sub=user_name,
        aud=["Auth_All"],
        jti=os.urandom(8).hex()
    )
    private_key = PRIVATE_KEY
    token = jwt.encode(claims.to_dict(), private_key, algorithm=ALGORITHM)
    return token


def parse_token(token_str):
    public_key = PUBLIC_KEY
    try:
        payload = jwt.decode(token_str, public_key, algorithms=[ALGORITHM], options={"verify_aud": False})
        return UserClaims(**payload), None
    except jwt.ExpiredSignatureError as e:
        payload = jwt.decode(token_str, public_key, algorithms=[ALGORITHM],
                             options={"verify_exp": False, "verify_aud": False})
        return UserClaims(**payload), e
    except Exception as e:
        return None, e


def save_user_token(token, user_id):
    expire = AUTH_TOKEN_EXPIRES * 3600 + 7 * 24 * 3600
    redis_client.set(USER_TOKEN_KEY % user_id, token, ex=expire)


def get_user_token_by_id(user_id):
    token = redis_client.get(USER_TOKEN_KEY % user_id)
    return token or ""


def clear_user_token(user_id):
    redis_client.delete(USER_TOKEN_KEY % user_id)
