from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from anime.anime_vod import AnimeVod
from demo.sql import get_session
from utils.response_util import ResponseUtil

anime_controller = APIRouter(prefix='/anime')


# ... 之前的代码 ...

class AnimeVodCreate(BaseModel):
    vod_name: str
    vod_play_url: Optional[dict] = {}


class AnimeVodUpdate(BaseModel):
    vod_name: Optional[str] = None
    vod_play_url: Optional[dict] = None


# 创建 AnimeVod
@anime_controller.post("/")
def create_anime_vod(
        anime_vod: AnimeVodCreate,
):
    with get_session() as session:
        db_anime_vod = AnimeVod(
            vod_name=anime_vod.vod_name,
            vod_play_url=anime_vod.vod_play_url
        )
        session.add(db_anime_vod)
        session.commit()
        session.refresh(db_anime_vod)
    return ResponseUtil.success(data=db_anime_vod, msg="创建成功")


# 更新 AnimeVod
@anime_controller.put("/{vod_id}")
def update_anime_vod(
        vod_id: int,
        anime_vod_update: AnimeVodUpdate,
):
    with get_session() as session:
        db_anime_vod = session.get(AnimeVod, vod_id)
        if not db_anime_vod:
            return ResponseUtil.error(msg="未找到该影片")

        if anime_vod_update.vod_name is not None:
            db_anime_vod.vod_name = anime_vod_update.vod_name
        if anime_vod_update.vod_play_url is not None:
            db_anime_vod.vod_play_url = anime_vod_update.vod_play_url

        db_anime_vod.updated_at = datetime.now()
        session.add(db_anime_vod)
        session.commit()
        session.refresh(db_anime_vod)
    return ResponseUtil.success(data=db_anime_vod, msg="更新成功")


# 根据 ID 获取单个 AnimeVod
@anime_controller.get("/{vod_id}")
def get_anime_vod(
        vod_id: int
):
    with get_session() as session:
        anime_vod = session.get(AnimeVod, vod_id)
        if not anime_vod:
            return ResponseUtil.error(msg="未找到该影片")
    return ResponseUtil.success(data=anime_vod, msg="获取成功")


# 获取所有 AnimeVod
@anime_controller.get("/", response_model=List[AnimeVod])
def get_anime_vods(
        offset: int = 0,
        limit: int = 100
):
    with get_session() as session:
        anime_vods = session.exec(select(AnimeVod).offset(offset).limit(limit)).all()
    return ResponseUtil.success(data=anime_vods, msg="获取成功")


# 删除 AnimeVod
@anime_controller.delete("/{vod_id}")
def delete_anime_vod(
        vod_id: int
):
    with get_session() as session:
        anime_vod = session.get(AnimeVod, vod_id)
        if not anime_vod:
            return ResponseUtil.error(msg="未找到该影片")

        session.delete(anime_vod)
        session.commit()
    return ResponseUtil.success(msg="删除成功")
