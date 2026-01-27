from __future__ import annotations

from flask import Blueprint
from flask.views import MethodView
from sqlalchemy import select

import ckan.plugins.toolkit as tk

import ckanext.tables.shared as t
from ckanext.ap_log import formatters as lf
from ckanext.ap_log.model import ApLogs
from ckanext.ap_main import formatters as f
from ckanext.ap_main.utils import ap_before_request
from ckanext.tables.shared import GenericTableView

ap_log = Blueprint("ap_log", __name__, url_prefix="/admin-panel")

ap_log.before_request(ap_before_request)


class LogsTable(t.TableDefinition):
    def __init__(self):
        super().__init__(
            name="logs",
            table_template="admin_panel/tables/table_base.html",
            data_source=t.DatabaseDataSource(
                stmt=select(
                    ApLogs.name.label("name"),
                    ApLogs.path.label("path"),
                    ApLogs.level.label("level"),
                    ApLogs.timestamp.label("timestamp"),
                    ApLogs.message.label("message"),
                ).order_by(ApLogs.timestamp.desc()),
            ),
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
            table_actions=[
                t.TableActionDefinition(
                    action="clear",
                    label="Clear logs",
                    callback=self._clear_logs,
                ),
            ],
        )

    def _clear_logs(self) -> t.ActionHandlerResult:
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
        "list", table=LogsTable, breadcrumb_label="Logs"
    ),
)

ap_log.add_url_rule("/reports/logs/clear", view_func=LogsClearView.as_view("clear"))
