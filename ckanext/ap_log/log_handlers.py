from __future__ import annotations

import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from ckan.plugins import toolkit as tk

from ckanext.ap_log.model import ApLogs

log = logging.getLogger(__name__)


class DatabaseHandler(logging.Handler):
    not_ready = False

    def __init__(self, db_uri: str):
        super().__init__()

        engine = create_engine(db_uri)
        inspector = inspect(engine)
        if not inspector.has_table(ApLogs.__tablename__):
            self.not_ready = True
            log.error("The ApLogs table is not initialized")

        session = sessionmaker(bind=engine)
        ApLogs.set_session(session())

    def emit(self, record: logging.LogRecord) -> None:
        if not tk.config:
            return

        if self.not_ready:
            return

        ApLogs.save_log(record, self.format(record))
