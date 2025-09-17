from typing import List, Optional
from pydantic import BaseModel


# 分类信息
class Category(BaseModel):
    id: Optional[int] = None
    pid: Optional[int] = None
    Pid: Optional[int] = None
    name: Optional[str] = None
    show: Optional[bool] = None


# 分类信息树形结构
class CategoryTree(Category):
    children: Optional[List['CategoryTree']] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


CategoryTree.update_forward_refs()
