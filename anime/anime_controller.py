# anime/anime_controller.py
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from anime.anime_dao import AnimeDao, ConfigPageQueryModel
from anime.anime_vod import AnimeVod
from plugin.db import pg_engine
from pydantic import BaseModel
from utils.response_util import ResponseUtil

from sqlmodel import Session, select
from typing import List, Optional

anime_controller = APIRouter(prefix='/anime')


# ... 之前的代码 ...

class AnimeVodCreate(BaseModel):
    vod_name: str
    vod_play_url: Optional[dict] = {}


class AnimeVodUpdate(BaseModel):
    vod_name: Optional[str] = None
    vod_play_url: Optional[dict] = None


# 添加新的 Pydantic 模型用于 upsert 和 search 接口
class AnimeVodUpsertRequest(BaseModel):
    name: str
    episode: str
    url: str


class AnimeVodSearchRequest(BaseModel):
    name: str
    episode: Optional[str] = None


# 新增或更新 AnimeVod 接口
@anime_controller.post("/upsert")
def upsert_anime_vod(anime_vod_request: AnimeVodUpsertRequest):
    from urllib.parse import urlparse

    name = anime_vod_request.name
    episode = anime_vod_request.episode
    url = anime_vod_request.url

    # 解析 URL 获取 host
    parsed_url = urlparse(url)
    host = parsed_url.hostname or "unknown"

    with Session(pg_engine) as session:
        # 根据名称查找现有的 AnimeVod 记录
        statement = select(AnimeVod).where(AnimeVod.vod_name == name)
        existing_anime_vod = session.exec(statement).first()

        if existing_anime_vod:
            # 如果存在记录，则更新
            vod_play_url = existing_anime_vod.vod_play_url or {}

            # 确保 host 字典存在
            if host not in vod_play_url:
                vod_play_url[host] = {}

            # 更新指定集数的 URL
            vod_play_url[host][episode] = url

            existing_anime_vod.vod_play_url = vod_play_url
            existing_anime_vod.updated_at = datetime.now()

            # 使用 SQLAlchemy 的 update 方式
            session.exec(
                AnimeVod.__table__.update().
                where(AnimeVod.vod_id == existing_anime_vod.vod_id).
                values(
                    vod_play_url=existing_anime_vod.vod_play_url,
                    updated_at=existing_anime_vod.updated_at
                )
            )
            session.commit()
            # 注意：使用 update() 后需要重新查询获取更新后的对象
            statement = select(AnimeVod).where(AnimeVod.vod_id == existing_anime_vod.vod_id)
            updated_anime_vod = session.exec(statement).first()

            return ResponseUtil.success(data=updated_anime_vod, msg="更新成功")
        else:
            # 如果不存在记录，则创建新记录
            vod_play_url = {host: {episode: url}}

            new_anime_vod = AnimeVod(
                vod_name=name,
                vod_play_url=vod_play_url
            )

            session.add(new_anime_vod)
            session.commit()
            session.refresh(new_anime_vod)

            return ResponseUtil.success(data=new_anime_vod, msg="创建成功")


# 根据 name 和 episode 查询 AnimeVod 并返回所有匹配的 URLs
@anime_controller.post("/search")
def search_anime_vod_by_name_and_episode(search_request: AnimeVodSearchRequest):
    name = search_request.name
    episode = search_request.episode

    with Session(pg_engine) as session:
        # 根据名称查找 AnimeVod 记录
        statement = select(AnimeVod).where(AnimeVod.vod_name == name)
        anime_vods = session.exec(statement).all()

        if not anime_vods:
            return ResponseUtil.error(msg="未找到该影片")

        # 收集所有匹配的 URLs
        if episode:
            urls = []
            for anime_vod in anime_vods:
                vod_play_url = anime_vod.vod_play_url or {}
                for host, episodes in vod_play_url.items():
                    if episode in episodes:
                        urls.append({
                            "host": host,
                            "url": episodes[episode]
                        })

            if not urls:
                return ResponseUtil.error(msg="该集数未找到")
            return ResponseUtil.success(data=urls, msg="查询成功")
        else:
            return ResponseUtil.success(data=anime_vods[0], msg="查询成功")


# 创建 AnimeVod
@anime_controller.post("/")
def create_anime_vod(
        anime_vod: AnimeVodCreate,
):
    with Session(pg_engine) as session:
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
    with Session(pg_engine) as session:
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
    with Session(pg_engine) as session:
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
    with Session(pg_engine) as session:
        anime_vods = session.exec(select(AnimeVod).offset(offset).limit(limit)).all()
    return ResponseUtil.success(data=anime_vods, msg="获取成功")


# 获取所有 AnimeVod
@anime_controller.post("/page", response_model=List[AnimeVod])
async def get_anime_vods(
        config_page_query: ConfigPageQueryModel
):
    with Session(pg_engine) as session:
        anime_vods = await AnimeDao.get_config_list(session, config_page_query, is_page=True)
    return ResponseUtil.success(data=anime_vods, msg="获取成功")


# 删除 AnimeVod
@anime_controller.delete("/{vod_id}")
def delete_anime_vod(
        vod_id: int
):
    with Session(pg_engine) as session:
        anime_vod = session.get(AnimeVod, vod_id)
        if not anime_vod:
            return ResponseUtil.error(msg="未找到该影片")

        session.delete(anime_vod)
        session.commit()
    return ResponseUtil.success(msg="删除成功")
