from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
from .movies import MovieUrlInfo, MovieDetail

# 搜索标签请求参数
class SearchTagsVO(BaseModel):
    pid: int
    cid: int
    plot: Optional[str] = None
    area: Optional[str] = None
    language: Optional[str] = None
    year: Optional[int] = None
    sort: Optional[str] = None

# 影视更新任务请求参数
class FilmCronVo(BaseModel):
    ids: List[str]
    time: int
    spec: str
    model: int
    state: bool
    remark: Optional[str] = None

# 定时任务数据response
class CronTaskVo(BaseModel):
    preV: Optional[str] = None  # 上次执行时间
    next: Optional[str] = None  # 下次执行时间

# 影视采集任务添加时需要的options
class FilmTaskOptions(BaseModel):
    id: str
    name: str

class Option(BaseModel):
    name: str
    value: Any

OptionGroup = Dict[str, List[Option]]

# 数据采集所需要的参数
class CollectParams(BaseModel):
    id: Optional[str] = None
    ids: Optional[List[str]] = None
    time: Optional[int] = None
    batch: Optional[bool] = None

# 影片信息搜索参数
class SearchVo(BaseModel):
    name: Optional[str] = None
    pid: Optional[int] = None
    cid: Optional[int] = None
    plot: Optional[str] = None
    area: Optional[str] = None
    language: Optional[str] = None
    year: Optional[int] = None
    remarks: Optional[str] = None
    beginTime: Optional[int] = None
    endTime: Optional[int] = None

# 多站点播放链接数据列表
class PlayLinkVo(BaseModel):
    id: str
    name: str
    linkList: List[MovieUrlInfo]

# 影片详情数据, 播放源合并版
class MovieDetailVo(BaseModel):
    movie_detail: MovieDetail
    list: List[PlayLinkVo]

# 用户信息返回对象
class UserInfoVo(BaseModel):
    id: int
    userName: str
    email: Optional[str] = None
    gender: Optional[int] = None
    nickName: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[int] = None

# 采集记录请求参数
class RecordRequestVo(BaseModel):
    originId: str
    collectType: int
    hour: int
    status: int
    beginTime: Optional[str] = None
    endTime: Optional[str] = None