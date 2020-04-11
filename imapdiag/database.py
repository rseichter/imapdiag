"""
This file is part of "imapdiag".

Copyright © 2020 Ralph Seichter
"""
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

_engine = None
Base = declarative_base()
Session = sessionmaker()


def init_db(url: str, clear: bool) -> None:
    global _engine
    if _engine is None:
        _engine = create_engine(url, echo=False)
        Session.configure(bind=_engine)
        Base.metadata.create_all(_engine)
        if clear:
            session = Session()
            session.query(ScanResult).delete(False)
            session.commit()


class ScanResult(Base):
    __tablename__ = 'scans'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ts = Column(DateTime, nullable=False)
    host = Column(String, nullable=False)
    user = Column(String, nullable=False)
    mailbox = Column(String, nullable=False)
    uid = Column(String, nullable=False)
    mid = Column(String, nullable=True)
    otherhost = Column(String, nullable=True)
    found = Column(Boolean, nullable=False, default=False)


def scan_result(host: str, user: str, mailbox: str, uid: str, mid: str, found: bool = False) -> ScanResult:
    result = ScanResult()
    result.found = found
    result.host = host
    result.mailbox = mailbox
    result.mid = mid
    result.ts = datetime.utcnow()
    result.uid = uid
    result.user = user.split('*')[0]
    return result
