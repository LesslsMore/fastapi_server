from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException
import re
import os
import json
from pathlib import Path

from ..config import data_config
from ..plugin.db import redis_client, db_engine
from ..plugin.common import util

# -------------------------------- 本地图库 --------------------------------

def create_file_table():
    """创建图片关联信息存储表"""
    if not exist_file_table():
        # 这里需要实现SQLAlchemy的表创建逻辑
        pass


def exist_file_table() -> bool:
    """判断图片表是否存在"""
    # 实现SQLAlchemy的表存在检查
    return False


def save_gallery(file_info: FileInfo):
    """保存图片关联信息"""
    # 实现SQLAlchemy的插入操作
    pass


def exist_file_info_by_rid(rid: int) -> bool:
    """通过关联ID检查图片是否存在"""
    # 实现SQLAlchemy的查询
    return False


def get_file_info_by_rid(rid: int) -> FileInfo:
    """通过关联ID获取图片信息"""
    # 实现SQLAlchemy的查询
    return FileInfo()


def get_file_info_by_id(id: int) -> FileInfo:
    """通过ID获取图片信息"""
    # 实现SQLAlchemy的查询
    return FileInfo()


def get_file_info_page(tl: List[str], page: dict) -> List[FileInfo]:
    """获取分页文件信息"""
    # 实现SQLAlchemy的分页查询
    return []


def del_file_info(id: int):
    """删除文件信息"""
    # 实现SQLAlchemy的删除
    pass


# -------------------------------- 图片同步 --------------------------------

def save_virtual_pic(pic_list: List[VirtualPicture]) -> bool:
    """保存待同步的图片信息到Redis"""
    try:
        zl = []
        for p in pic_list:
            m = json.dumps(p.dict())
            zl.append({"score": float(p.id), "member": m})
        redis_client.zadd(data_config.VIRTUAL_PICTURE_KEY, *zl)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存虚拟图片失败: {str(e)}")


def sync_film_picture():
    """同步新采集入站还未同步的图片"""
    count = redis_client.zcard(data_config.VIRTUAL_PICTURE_KEY)
    if count <= 0:
        return

    sl = redis_client.zpopmax(data_config.VIRTUAL_PICTURE_KEY, data_config.MAX_SCAN_COUNT)
    if not sl:
        return

    for s in sl:
        vp = VirtualPicture(**json.loads(s["member"]))
        if exist_file_info_by_rid(vp.id):
            continue

        try:
            file_name = util.save_online_file(vp.link, data_config.FILM_PICTURE_UPLOAD_DIR)
            save_gallery(FileInfo(
                link=f"{data_config.FILM_PICTURE_ACCESS}{file_name}",
                uid=data_config.USER_ID_INITIAL_VAL,
                relevance_id=vp.id,
                type=0,
                fid=re.sub(r'\.[^.]+$', '', file_name),
                file_type=Path(file_name).suffix[1:].lower()
            ))
        except Exception:
            continue

    sync_film_picture()


def replace_detail_pic(d: dict):
    """替换影片详情中的图片地址"""
    if exist_file_info_by_rid(d["id"]):
        f = get_file_info_by_rid(d["id"])
        d["picture"] = f.link


def replace_basic_detail_pic(d: dict):
    """替换影片基本数据中的封面图"""
    if exist_file_info_by_rid(d["id"]):
        f = get_file_info_by_rid(d["id"])
        d["picture"] = f.link