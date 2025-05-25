from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime



class FileInfo(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    link: str
    uid: int
    relevance_id: int
    type: int  # 0: 影片封面, 1: 用户头像
    fid: str
    file_type: str  # txt, png, jpg

    class Config:
        orm_mode = True


class VirtualPicture(BaseModel):
    id: int
    link: str