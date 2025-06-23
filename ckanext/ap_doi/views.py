from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.editable_config.shared import value_as_string

import ckanext.ap_main.table as table
import ckanext.ap_main.types as types
from ckanext.ap_main.utils import ap_before_request, get_config_schema
from ckanext.ap_main.views.generics import ApConfigurationPageView, ApTableView

log = logging.getLogger(__name__)
doi_dashboard = Blueprint("doi_dashboard", __name__, url_prefix="/admin-panel/doi")
doi_dashboard.before_request(ap_before_request)


class DoiTable(table.TableDefinition):
    def __init__(self):
        super().__init__(
            name="doi",
            ajax_url=tk.url_for("doi_dashboard.list", data=True),
            placeholder=tk._("No DOIs found"),
            columns=[
                table.ColumnDefinition("id", visible=False, filterable=False),
                table.ColumnDefinition("title", min_width=300),
                table.ColumnDefinition("doi_status", min_width=100),
                table.ColumnDefinition("identifier", min_width=200),
                table.ColumnDefinition(
                    "timestamp",
                    formatters=[("date", {"date_format": "%Y-%m-%d %H:%M"})],
                    min_width=150,
                ),
                table.ColumnDefinition(
                    "published",
                    formatters=[("date", {"date_format": "%Y-%m-%d %H:%M"})],
                    min_width=150,
                ),
                table.ColumnDefinition(
                    "actions",
                    formatters=[("actions", {})],
                    filterable=False,
                    tabulator_formatter="html",
                    sorter=None,
                    resizable=False,
                ),
            ],
            actions=[
                table.ActionDefinition(
                    "update",
                    icon="fa fa-refresh",
                    endpoint="doi_dashboard.create_or_update_doi",
                    url_params={"package_id": "$id"},
                ),
                table.ActionDefinition(
                    "view",
                    icon="fa fa-eye",
                    endpoint="ap_content.entity_proxy",
                    url_params={
                        "view": "read",
                        "entity_type": "$type",
                        "entity_id": "$name",
                    },
                ),
            ],
            global_actions=[
                table.GlobalActionDefinition(
                    action="update_doi", label="Update DOI for selected packages"
                ),
            ],
        )

    def get_raw_data(self) -> list[dict[str, Any]]:
        return tk.get_action("ap_doi_get_packages_doi")({"ignore_auth": True}, {})


class ApConfigurationDisplayPageView(MethodView):
    def get(self):
        self.schema = get_config_schema("ap_doi_config")
        data = self.get_config_form_data()

        return tk.render(
            "ap_example/display_config.html",
            extra_vars={"schema": self.schema, "data": data},
        )

    def get_config_form_data(self) -> dict[str, Any]:
        """Fetch/humanize configuration values from a CKANConfig"""

        data = {}

        if not self.schema:
            return data

        for field in self.schema["fields"]:
            if field["field_name"] not in tk.config:
                continue

            data[field["field_name"]] = value_as_string(
                field["field_name"], tk.config[field["field_name"]]
            )

        return data


class ApDoiView(ApTableView):
    def get_global_action(self, value: str) -> types.GlobalActionHandler | None:
        return {
            "update_doi": self._create_or_update_doi,
        }.get(value)

    @staticmethod
    def _create_or_update_doi(row: types.Row) -> types.GlobalActionHandlerResult:
        try:
            result = tk.get_action("ap_doi_update_doi")({}, {"package_id": row["id"]})
            if result["status"] == "error":
                for err in result["errors"]:
                    return False, err
            else:
                return True, result["message"]
        except Exception:
            return False, "Error updating DOI"

        return True, None


def create_or_update_doi(package_id: str):
    try:
        result = tk.get_action("ap_doi_update_doi")({}, {"package_id": package_id})
        if result["status"] == "error":
            for err in result["errors"]:
                tk.h.flash_error(err)
        else:
            tk.h.flash_success(result["message"])
    except Exception:
        pass

    return tk.h.redirect_to("doi_dashboard.list")


doi_dashboard.add_url_rule("/update_doi/<package_id>", view_func=create_or_update_doi)
doi_dashboard.add_url_rule(
    "/list",
    view_func=ApDoiView.as_view(
        "list",
        table=DoiTable,
        breadcrumb_label="DOI dashboard",
        page_title="DOI dashboard",
    ),
)

doi_dashboard.add_url_rule(
    "/config",
    view_func=ApConfigurationPageView.as_view("config", "ap_doi_config"),
)
