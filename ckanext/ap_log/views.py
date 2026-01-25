from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk
import ckanext.tables.shared as t
from ckan import model

from ckanext.ap_log.model import ApLogs
from ckanext.ap_log import formatters as lf
from ckanext.ap_main import formatters as f
from ckanext.tables.shared import GenericTableView

ap_log = Blueprint("ap_log", __name__, url_prefix="/admin-panel")
ap_before_request_func = tk.get_action("ap_before_request_action") if tk.asbool(tk.config.get("ckan.admin_panel.register_action", False)) else None
# Wait, ap_before_request was imported from util.
from ckanext.ap_main.utils import ap_before_request
ap_log.before_request(ap_before_request)


class LogsTable(t.TableDefinition):
    def __init__(self):
        super().__init__(
            name="logs",
            ajax_url=tk.url_for("ap_log.list", data=True),
            placeholder="No logs found",
            # table_action_snippet="ap_log/table_actions.html", # ckanext-tables doesn't support this directly in __init__ usually, handled in template
            columns=[
                t.ColumnDefinition(field="name", min_width=150),
                t.ColumnDefinition(
                    field="path",
                    min_width=200,
                    formatters=[(f.ShortenPathFormatter, {"max_length": 50})],
                ),
                t.ColumnDefinition(
                    field="level",
                    formatters=[(lf.LogLevelFormatter, {})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(
                    field="timestamp",
                    formatters=[(f.DateFormatter, {"date_format": "%Y-%m-%d %H:%M"})],
                ),
                t.ColumnDefinition(field="message", min_width=300),
            ],
            bulk_actions=[
                 t.BulkActionDefinition(
                    action="clear",
                    label="Clear logs",
                    callback=self._clear_logs,
                ),
            ]
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

    def _clear_logs(self, rows: list[t.Row]) -> t.ActionHandlerResult:
        # This clears all logs regardless of selection, preserving legacy behavior?
        # Or should it only delete selected rows?
        # ApLogs uses a table defined in model.py. ApLogs.clear_logs() truncates it.
        # If I want to delete specific rows, I need IDs. But get_raw_data doesn't select IDs?
        # The query does not select IDs!
        # Legacy code didn't use IDs either?
        # Legacy code: _clear_logs(row: Row). ApLogs.clear_logs().
        # So yes, it clears everything.

        ApLogs.clear_logs()
        return t.ActionHandlerResult(success=True, message="All logs have been cleared")


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
    view_func=GenericTableView.as_view(
        "list",
        table=LogsTable,
        breadcrumb_label="Logs",
        page_title="System Logs"
    ),
)

ap_log.add_url_rule("/reports/logs/clear", view_func=LogsClearView.as_view("clear"))
