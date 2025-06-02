from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, ClassVar, cast
from unittest import mock

from sqlalchemy import Column, DateTime, Integer, Text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query, Session

from ckan.model.types import make_uuid
from ckan.plugins import toolkit as tk

log = logging.getLogger(__name__)


class ApLogs(tk.BaseModel):  # type: ignore
    __tablename__ = "ap_logs"
    session: ClassVar[Session] = mock.MagicMock()

    id = Column(Text, primary_key=True, default=make_uuid)

    name = Column(Text)
    path = Column(Text)
    level = Column(Integer)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    message = Column(Text)
    message_formatted = Column(Text)

    @classmethod
    def all(cls) -> list[dict[str, Any]]:
        query: Query = cls.get_session().query(cls).order_by(cls.timestamp.desc())

        return [log.dictize({}) for log in query.all()]

    @classmethod
    def save_log(cls, record: logging.LogRecord, message_formatted: str) -> None:
        cls.get_session().add(
            cls(
                name=record.name,
                path=record.pathname,
                level=record.levelno,
                message=record.getMessage(),
                message_formatted=message_formatted,
            )
        )
        cls.get_session().commit()

    def dictize(self, context):
        return {
            "name": self.name,
            "path": self.path,
            "level": self.level,
            "timestamp": self.timestamp,
            "message": self.message,
            "message_formatted": self.message_formatted,
        }

    @classmethod
    def clear_logs(cls) -> int:
        rows_deleted = cls.get_session().query(cls).delete()
        cls.get_session().commit()

        return rows_deleted

    @classmethod
    def set_session(cls, session: Session):
        cls.session = session

    @classmethod
    def get_session(cls) -> Session:
        return cls.session

    @classmethod
    def table_initialized(cls) -> bool:
        if not cls.session:
            return False

        engine = cast(Engine, cls.session.get_bind())

        return inspect(engine).has_table(cls.__tablename__)
