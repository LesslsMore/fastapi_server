from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field

from anime.anime_vod import AnimeVod
from utils.page_util import PageUtil


# @as_query
class ConfigPageQueryModel(SQLModel):
    """
    参数配置管理分页查询模型
    """

    page_num: Optional[int] = Field(default=1, description='当前页码')
    page_size: Optional[int] = Field(default=10, description='每页记录数')


class AnimeDao:
    @classmethod
    async def get_config_list(cls, db: AsyncSession, query_object: ConfigPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取参数配置列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 参数配置列表信息对象
        """
        query = (
            select(AnimeVod)
            .order_by(AnimeVod.vod_id)
        )
        config_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return config_list
