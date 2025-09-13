from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from anime.anime_vod import AnimeVod, anime_vod_dao
from config.constant import IOrderEnum
from dao.base_dao import ConfigPageQueryModel
from demo.sql import get_session
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/anime')


# 添加新的 Pydantic 模型用于 upsert 和 search 接口
class AnimeVodUpsertRequest(BaseModel):
    vod_id: int
    name: str
    episode: str
    url: str
    vod_pic: str


class AnimeVodSearchRequest(BaseModel):
    name: str
    episode: Optional[str] = None


# 新增或更新 AnimeVod 接口
@router.post("/upsert")
def upsert_anime_vod(anime_vod_request: AnimeVodUpsertRequest):
    from urllib.parse import urlparse

    name = anime_vod_request.name
    episode = anime_vod_request.episode
    url = anime_vod_request.url
    vod_pic = anime_vod_request.vod_pic
    vod_id = anime_vod_request.vod_id

    # 解析 URL 获取 host
    parsed_url = urlparse(url)
    host = parsed_url.hostname or "unknown"

    with get_session() as session:
        # 根据名称查找现有的 AnimeVod 记录
        statement = select(AnimeVod).where(AnimeVod.vod_id == vod_id)
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
                    vod_pic=vod_pic,
                    updated_at=existing_anime_vod.updated_at
                )
            )

            # 注意：使用 update() 后需要重新查询获取更新后的对象
            statement = select(AnimeVod).where(AnimeVod.vod_id == existing_anime_vod.vod_id)
            updated_anime_vod = session.exec(statement).first()

            return ResponseUtil.success(data=updated_anime_vod, msg="更新成功")
        else:
            # 如果不存在记录，则创建新记录
            vod_play_url = {host: {episode: url}}

            new_anime_vod = AnimeVod(
                vod_id=vod_id,
                vod_name=name,
                vod_play_url=vod_play_url,
                vod_pic=vod_pic,
            )

            session.add(new_anime_vod)

            session.refresh(new_anime_vod)

            return ResponseUtil.success(data=new_anime_vod, msg="创建成功")


# 根据 name 和 episode 查询 AnimeVod 并返回所有匹配的 URLs
@router.post("/search")
def search_anime_vod_by_name_and_episode(search_request: AnimeVodSearchRequest):
    name = search_request.name
    episode = search_request.episode

    anime_vod = anime_vod_dao.query_item(filter_dict={"vod_name": name})

    if not anime_vod:
        return ResponseUtil.error(msg="未找到该影片")

    # 收集所有匹配的 URLs
    if episode:
        urls = []

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
        return ResponseUtil.success(data=anime_vod, msg="查询成功")


# 获取所有 AnimeVod
@router.post("/page", response_model=List[AnimeVod])
async def get_anime_vods(
        config_page_query: ConfigPageQueryModel
):
    anime_vods = anime_vod_dao.page_items({}, ['vod_id'], IOrderEnum.descendent, config_page_query)
    # with get_session() as session:
    #     anime_vods = await AnimeDao.get_config_list(session, config_page_query, is_page=True)
    return ResponseUtil.success(data=anime_vods, msg="获取成功")
