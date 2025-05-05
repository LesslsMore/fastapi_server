from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException
import re
import os
import json
from pathlib import Path

from config import data_config
from plugin.db import redis_client


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