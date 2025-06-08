from typing import Optional, List
from sqlmodel import Field, SQLModel, Session, select

from model.collect.MacType import MacType
from plugin.db import get_session, pg_engine


class MacTypeDao:

    @staticmethod
    def get_mac_type_list() -> List[MacType]:
        with Session(pg_engine) as session:
            statement = select(MacType).where(MacType.type_status == 1)
            results = session.exec(statement).all()
            return results

