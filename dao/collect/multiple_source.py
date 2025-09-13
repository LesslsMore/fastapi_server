import json
import logging
from typing import List, Optional

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import SQLModel, Field, select

from dao.system.movies import generate_hash_key
from demo.sql import get_session
from model.collect.MacVod import MacVod
from model.system.movies import MovieUrlInfo
from plugin.common.conver.mac_vod import mac_vod_list_to_movie_detail_list


class MultipleSourceModel(SQLModel, table=True):
    __tablename__ = 'multiple_source'
    id: int = Field(primary_key=True)
    site_id: Optional[str]
    key: Optional[str]
    playList: Optional[List[MovieUrlInfo]] = Field(default_factory=list, sa_column=Column(JSON))
    __table_args__ = (
        UniqueConstraint('site_id', 'key', name='uq_site_key'),
        # {"sqlite_autoincrement": True},
        # # 添加唯一约束
        # SQLModel.metadata.tables["multiple_source"].unique_constraint("uq_site_key", "site_id", "key") if hasattr(
        #     SQLModel.metadata.tables["multiple_source"], "unique_constraint") else None
    )


def save_site_play_list(site_id: str, mac_vod_list: List[MacVod]):
    movie_detail_list = mac_vod_list_to_movie_detail_list(mac_vod_list)
    try:
        res = {}
        for movie_detail in movie_detail_list:
            if movie_detail.playList and len(movie_detail.playList) > 0:
                data = json.dumps([item.dict() for item in movie_detail.playList[0]])
                if movie_detail.descriptor.cName and "解说" in movie_detail.descriptor.cName:
                    continue
                if movie_detail.descriptor.dbId:
                    res[generate_hash_key(movie_detail.descriptor.dbId)] = data
                res[generate_hash_key(movie_detail.name)] = data
        if res:
            for key, val in res.items():
                with get_session() as session:
                    values = {"site_id": site_id, "key": key, "playList": val}
                    stmt = insert(MultipleSourceModel).values(**values)
                    update_dict = {"playList": stmt.excluded["playList"]}
                    stmt = stmt.on_conflict_do_update(
                        index_elements=[MultipleSourceModel.site_id, MultipleSourceModel.key], set_=update_dict)
                    session.exec(stmt)
                    session.commit()

    except Exception as e:
        logging.info(f"save_site_play_list Error: {e}")


def get_multiple_play(site_id: str, key: str) -> Optional[List[MovieUrlInfo]]:
    with get_session() as session:
        statement = select(MultipleSourceModel).where(MultipleSourceModel.site_id == site_id,
                                                      MultipleSourceModel.key == key)
        results = session.exec(statement)
        item = results.first()
        if item:
            play_list = json.loads(item.playList)
            return [MovieUrlInfo(**item) for item in play_list]
        return None
