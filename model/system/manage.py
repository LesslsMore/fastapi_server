from typing import List
from pydantic import BaseModel

class BasicConfig(BaseModel):
    siteName: str
    domain: str
    logo: str
    keyword: str
    describe: str
    state: bool
    hint: str

class Banner(BaseModel):
    id: str
    mid: int
    name: str
    year: int
    cName: str
    poster: str
    picture: str
    remark: str
    sort: int