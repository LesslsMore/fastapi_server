from typing import List, Optional
from sqlmodel import Session, select
from model.system.failure_record import FailureRecord

from datetime import datetime

from plugin.db import get_session


def create_failure_record_table():
    session = get_session()
    FailureRecord.metadata.create_all(session.get_bind())

def save_failure_record(fr: FailureRecord):
    session = get_session()
    session.add(fr)
    session.commit()

def failure_record_list(origin_id: Optional[str] = None, status: Optional[int] = None, begin_time: Optional[datetime] = None, end_time: Optional[datetime] = None, page: int = 1, page_size: int = 20) -> List[FailureRecord]:
    session = get_session()
    stmt = select(FailureRecord)
    if origin_id:
        stmt = stmt.where(FailureRecord.origin_id == origin_id)
    if status is not None:
        stmt = stmt.where(FailureRecord.status == status)
    if begin_time and end_time:
        stmt = stmt.where(FailureRecord.created_at.between(begin_time, end_time))
    stmt = stmt.order_by(FailureRecord.updated_at.desc()).offset((page-1)*page_size).limit(page_size)
    return session.exec(stmt).all()

def find_record_by_id(id: int) -> Optional[FailureRecord]:
    session = get_session()
    return session.get(FailureRecord, id)

def change_record(fr: FailureRecord, status: int):
    session = get_session()
    fr.status = status
    fr.updated_at = datetime.utcnow()
    session.add(fr)
    session.commit()

def del_done_record():
    session = get_session()
    session.exec(select(FailureRecord).where(FailureRecord.status == 0)).delete()
    session.commit()

def truncate_record_table():
    session = get_session()
    session.exec(f'TRUNCATE TABLE {FailureRecord.__tablename__}')
    session.commit()