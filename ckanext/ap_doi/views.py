from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.editable_config.shared import value_as_string

import ckanext.tables.shared as t
from ckanext.ap_main.utils import ap_before_request, get_config_schema
from ckanext.ap_main.views.generics import ApConfigurationPageView
from ckanext.ap_main import formatters as f
from ckanext.tables.shared import GenericTableView

log = logging.getLogger(__name__)
doi_dashboard = Blueprint("doi_dashboard", __name__, url_prefix="/admin-panel/doi")
doi_dashboard.before_request(ap_before_request)


class DoiTable(t.TableDefinition):
    def __init__(self):
        super().__init__(
            name="doi",
            ajax_url=tk.url_for("doi_dashboard.list", data=True),
            placeholder=tk._("No DOIs found"),
            columns=[
                t.ColumnDefinition(field="title", min_width=300),
                t.ColumnDefinition(field="doi_status", min_width=100),
                t.ColumnDefinition(field="identifier", min_width=200),
                t.ColumnDefinition(
                    field="timestamp",
                    formatters=[(f.DateFormatter, {"date_format": "%Y-%m-%d %H:%M"})],
                    min_width=150,
                ),
                t.ColumnDefinition(
                    field="published",
                    formatters=[(f.DateFormatter, {"date_format": "%Y-%m-%d %H:%M"})],
                    min_width=150,
                ),
                t.ColumnDefinition(
                    field="actions",
                    formatters=[(f.ActionsFormatter, {})],
                    searchable=False,
                    tabulator_formatter="html",
                    sortable=False,
                    resizable=False,
                ),
            ],
            row_actions=[
                t.RowActionDefinition(
                    action="update",
                    icon="fa fa-refresh",
                    url=lambda row: tk.url_for(
                        "doi_dashboard.create_or_update_doi", package_id=row["id"]
                    ),
                ),
                t.RowActionDefinition(
                    action="view",
                    icon="fa fa-eye",
                    url=lambda row: tk.url_for(
                        "ap_content.entity_proxy",
                        view="read",
                        entity_type=row["type"],
                        entity_id=row["name"],
                    ),
                ),
            ],
            bulk_actions=[
                t.BulkActionDefinition(
                    action="update_doi",
                    label="Update DOI for selected packages",
                    callback=self._create_or_update_doi,
                ),
            ],
        )

    def get_raw_data(self) -> list[dict[str, Any]]:
        return tk.get_action("ap_doi_get_packages_doi")({"ignore_auth": True}, {})

    def _create_or_update_doi(self, rows: list[t.Row]) -> t.ActionHandlerResult:
        errors = []
        for row in rows:
            try:
                result = tk.get_action("ap_doi_update_doi")({}, {"package_id": row["id"]})
                if result["status"] == "error":
                    for err in result["errors"]:
                        errors.append(err)
            except Exception:
                errors.append(f"Error updating DOI for {row.get('title', row['id'])}")

        if errors:
            return t.ActionHandlerResult(success=False, error="\n".join(errors))

        return t.ActionHandlerResult(success=True, message="DOI updated for selected packages")


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
    view_func=GenericTableView.as_view(
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
