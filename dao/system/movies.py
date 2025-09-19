import hashlib
import re
from typing import Union


def generate_hash_key(key: Union[str, int]) -> str:
    m_name = str(key)
    m_name = re.sub(r"\s", "", m_name)
    m_name = re.sub(r"～.*～$", "", m_name)
    m_name = re.sub(r"^[\W_]+|[\W_]+$", "", m_name)
    m_name = re.sub(r"季.*", "季", m_name)
    h = hashlib.md5()
    h.update(m_name.encode("utf-8"))
    return h.hexdigest()
