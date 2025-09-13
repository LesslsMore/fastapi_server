from typing import List

from sqlmodel import select

from demo.sql import get_session
from model.collect.MacType import MacType


class MacTypeDao:

    @staticmethod
    def get_mac_type_list() -> List[MacType]:
        with get_session() as session:
            statement = select(MacType).where(MacType.type_status == 1)
            results = session.exec(statement).all()
            return results
