from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel

# 数据模型定义
class Movie(BaseModel):
    id: int
    name: str
    cid: int
    cname: str
    en_name: Optional[str] = None
    time: Optional[str] = None
    remarks: Optional[str] = None
    play_from: Optional[str] = None

class MovieDescriptor(BaseModel):
    subTitle: Optional[str] = None
    cName: Optional[str] = None
    enName: Optional[str] = None
    initial: Optional[str] = None
    classTag: Optional[str] = None
    actor: Optional[str] = None
    director: Optional[str] = None
    writer: Optional[str] = None
    blurb: Optional[str] = None
    remarks: Optional[str] = None
    releaseDate: Optional[str] = None
    area: Optional[str] = None
    language: Optional[str] = None
    year: Optional[str] = None
    state: Optional[str] = None
    updateTime: Optional[str] = None
    addTime: Optional[int] = None
    dbId: Optional[int] = None
    dbScore: Optional[str] = None
    hits: Optional[int] = None
    content: Optional[str] = None

class MovieBasicInfo(BaseModel):
    id: int
    cid: int
    pid: Optional[int] = None
    name: str
    sub_title: Optional[str] = None
    c_name: Optional[str] = None
    state: Optional[str] = None
    picture: Optional[str] = None
    actor: Optional[str] = None
    director: Optional[str] = None
    blurb: Optional[str] = None
    remarks: Optional[str] = None
    area: Optional[str] = None
    year: Optional[str] = None

class MovieUrlInfo(BaseModel):
    episode: Optional[str] = None
    link: Optional[str] = None

class MovieDetail(BaseModel):
    id: int
    cid: int
    pid: Optional[int] = None
    name: str
    picture: Optional[str] = None
    playFrom: Optional[List[str]] = None
    DownFrom: Optional[str] = None
    playList: Optional[List[List[MovieUrlInfo]]] = None
    downloadList: Optional[List[List[MovieUrlInfo]]] = None
    descriptor: Optional[MovieDescriptor] = None
    # 兼容 Go 端结构
    # sub_title: Optional[str] = None
    # c_name: Optional[str] = None
    # class_tag: Optional[str] = None
    # area: Optional[str] = None
    # language: Optional[str] = None
    # year: Optional[str] = None
    # initial: Optional[str] = None
    # db_score: Optional[str] = None
    # hits: Optional[int] = None
    # update_time: Optional[str] = None
    # add_time: Optional[int] = None
    # state: Optional[str] = None
    # remarks: Optional[str] = None
    # release_date: Optional[str] = None
    # db_id: Optional[int] = None