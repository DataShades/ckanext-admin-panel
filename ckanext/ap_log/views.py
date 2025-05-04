from __future__ import annotations

from typing import Union

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.ap_log.model import ApLogs

from ckanext.ap_main.utils import ap_before_request

ap_log = Blueprint("ap_log", __name__, url_prefix="/admin-panel")
ap_log.before_request(ap_before_request)


class ReportLogsView(MethodView):
    def get(self) -> Union[str, Response]:
        if not ApLogs.table_initialized():
            return tk.render("ap_log/logs_disabled.html")

        return tk.render("ap_log/logs.html", extra_vars={})

    def post(self) -> Response:
        if "clear_logs" in tk.request.form:
            ApLogs.clear_logs()
            tk.h.flash_success(tk._("Logs have been cleared."))

        return tk.redirect_to("ap_log.list")


ap_log.add_url_rule("/reports/logs", view_func=ReportLogsView.as_view("list"))
