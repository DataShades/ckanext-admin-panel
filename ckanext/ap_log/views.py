from __future__ import annotations

from typing import Any

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.ap_log.model import ApLogs

import ckanext.ap_main.types as types
from ckanext.ap_main.table import ColumnDefinition, TableDefinition
from ckanext.ap_main.types import GlobalActionHandlerResult, Row
from ckanext.ap_main.utils import ap_before_request
from ckanext.ap_main.views.generics import ApTableView

ap_log = Blueprint("ap_log", __name__, url_prefix="/admin-panel")
ap_log.before_request(ap_before_request)


class LogsTable(TableDefinition):
    def __init__(self):
        super().__init__(
            name="logs",
            ajax_url=tk.url_for("ap_log.list", data=True),
            placeholder="No logs found",
            table_action_snippet="ap_log/table_actions.html",
            columns=[
                ColumnDefinition(field="name", min_width=150),
                ColumnDefinition(
                    field="path",
                    min_width=200,
                    formatters=[("shorten_path", {"max_length": 50})],
                ),
                ColumnDefinition(
                    field="level",
                    formatters=[("log_level", {})],
                    tabulator_formatter="html",
                ),
                ColumnDefinition(
                    field="timestamp",
                    formatters=[("date", {"date_format": "%Y-%m-%d %H:%M"})],
                ),
                ColumnDefinition(field="message", min_width=300),
            ],
        )

    def get_raw_data(self) -> list[dict[str, Any]]:
        if not ApLogs.table_initialized():
            return []

        query = model.Session.query(
            ApLogs.name.label("name"),
            ApLogs.path.label("path"),
            ApLogs.level.label("level"),
            ApLogs.timestamp.label("timestamp"),
            ApLogs.message.label("message"),
        ).order_by(ApLogs.timestamp.desc())

        columns = ["name", "path", "level", "timestamp", "message"]

        return [dict(zip(columns, row)) for row in query.all()]


class LogsView(ApTableView):
    def get_global_action(self, value: str) -> types.GlobalActionHandler | None:
        return {"clear": self._clear_logs}.get(value)

    @staticmethod
    def _clear_logs(row: Row) -> GlobalActionHandlerResult:
        ApLogs.clear_logs()
        return True, None


class LogsClearView(MethodView):
    def post(self) -> str:
        if not ApLogs.table_initialized():
            tk.h.flash_error("The logs table is not initialized")
            return ""

        ApLogs.clear_logs()
        tk.h.flash_success("All logs have been cleared")
        return ""


ap_log.add_url_rule(
    "/reports/logs",
    view_func=LogsView.as_view(
        "list", table=LogsTable, breadcrumb_label="Logs", page_title="System Logs"
    ),
)

ap_log.add_url_rule("/reports/logs/clear", view_func=LogsClearView.as_view("clear"))
