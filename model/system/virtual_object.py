from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, validator, field_validator
from pydantic_core.core_schema import ValidationInfo

from model.system.movies import MovieUrlInfo, MovieDetail
from model.system.response import Page


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
    paging: Optional[Page] = None
    current: Optional[int] = None  # 添加独立的分页参数
    pageSize: Optional[int] = None  # 添加独立的分页参数

    # 整数类型转换验证器
    # 分页参数调整（使用field_validator）
    @field_validator('paging', mode='after')
    def adjust_paging(cls, v: Page, info: ValidationInfo) -> Page:
        """将独立的current/pageSize参数映射到paging对象"""
        data = info.data
        if data.get('current') or data.get('pageSize'):
            current = data.get('current', 1)
            pageSize = data.get('pageSize', 10)
            # 确保分页参数在有效范围内
            pageSize = max(1, min(pageSize, 500))
            return Page(current=current, pageSize=pageSize)
        return v

    # 整数ID转换验证器
    @field_validator('pid', 'cid', mode='before')
    def convert_ids(cls, v) -> int:
        if v in ["", None]: return 0
        try:
            return int(v)
        except:
            raise ValueError("ID必须为整数")

    # 年份转换验证器
    @field_validator('year', mode='before')
    def convert_year(cls, v) -> Optional[int]:
        if v in ["", None]: return None
        try:
            return int(v) if v else None
        except:
            raise ValueError("年份必须为整数")

    # 时间戳转换验证器
    @field_validator('beginTime', 'endTime', mode='before')
    def convert_timestamps(cls, v) -> Optional[int]:
        if v in ["", None]: return None
        try:
            return int(datetime.strptime(v, "%Y-%m-%d %H:%M:%S").timestamp())
        except:
            raise ValueError("时间格式应为 YYYY-MM-DD HH:MM:SS")

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
