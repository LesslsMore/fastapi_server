from datetime import datetime
from typing import List, Optional

from sqlmodel import select

from demo.sql import get_session
from model.system.failure_record import FailureRecord


class FailureRecordService:
    @staticmethod
    def create_failure_record_table():
        with get_session() as session:
            FailureRecord.metadata.create_all(session.get_bind())

    @staticmethod
    def save_failure_record(fr: FailureRecord):
        with get_session() as session:
            session.add(fr)
            session.commit()

    @staticmethod
    def failure_record_list(origin_id: Optional[str] = None, status: Optional[int] = None,
                            begin_time: Optional[datetime] = None, end_time: Optional[datetime] = None, page: int = 1,
                            page_size: int = 20) -> List[FailureRecord]:
        with get_session() as session:
            stmt = select(FailureRecord)
            if origin_id:
                stmt = stmt.where(FailureRecord.origin_id == origin_id)
            if status is not None:
                stmt = stmt.where(FailureRecord.status == status)
            if begin_time and end_time:
                stmt = stmt.where(FailureRecord.created_at.between(begin_time, end_time))
            stmt = stmt.order_by(FailureRecord.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
            return session.exec(stmt).all()

    @staticmethod
    def find_record_by_id(id: int) -> Optional[FailureRecord]:
        with get_session() as session:
            return session.get(FailureRecord, id)

    @staticmethod
    def change_record(fr: FailureRecord, status: int):
        with get_session() as session:
            fr.status = status
            fr.updated_at = datetime.now()
            session.add(fr)
            session.commit()

    @staticmethod
    def del_done_record():
        with get_session() as session:
            session.exec(select(FailureRecord).where(FailureRecord.status == 0)).delete()
            session.commit()

    @staticmethod
    def truncate_record_table():
        with get_session() as session:
            session.exec(f'TRUNCATE TABLE {FailureRecord.__tablename__}')
            session.commit()
