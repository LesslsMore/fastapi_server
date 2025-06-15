import os
import binascii
import hashlib


def generate_salt() -> str:
    """
    生成 length为16的随机字符串 (16进制表示)
    :return: 16字符的随机字符串
    """
    # 生成8个随机字节
    random_bytes = os.urandom(8)
    # 将字节转换为16进制字符串，结果长度为 8 * 2 = 16
    salt = binascii.hexlify(random_bytes).decode('utf-8')
    return salt


def password_encrypt(password: str, salt: str) -> str:
    """
    密码加密 , (password+salt) md5 * 3
    :param password: 密码字符串
    :param salt: 盐值字符串
    :return: 加密后的密码字符串
    """
    b = (password + salt).encode('utf-8')
    for _ in range(3):
        b = hashlib.md5(b).hexdigest().encode('utf-8')
    return b.decode('utf-8')
