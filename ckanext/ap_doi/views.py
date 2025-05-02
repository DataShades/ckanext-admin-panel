from __future__ import annotations

import logging
from typing import Any, Callable, Union

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.logic import parse_params

from ckanext.collection.shared import get_collection
from ckanext.editable_config.shared import value_as_string

from ckanext.ap_main.utils import ap_before_request, get_config_schema
from ckanext.ap_main.views.generics import ApConfigurationPageView

log = logging.getLogger(__name__)
doi_dashboard = Blueprint("doi_dashboard", __name__, url_prefix="/admin-panel/doi")
doi_dashboard.before_request(ap_before_request)


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


class ApDoiView(MethodView):
    def get(self) -> Union[str, Response]:

        return tk.render(
            "ap_doi/list.html",
            extra_vars={
                "collection": get_collection("ap-doi", parse_params(tk.request.args)),
            },
        )

    def post(self) -> Response:
        bulk_action = tk.request.form.get("bulk-action")
        package_ids = tk.request.form.getlist("entity_id")

        action_func = self._get_bulk_action(bulk_action) if bulk_action else None

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("doi_dashboard.list")

        for package_id in package_ids:
            try:
                action_func(package_id)
            except tk.ValidationError as e:
                tk.h.flash_error(str(e))

        return tk.redirect_to("doi_dashboard.list")

    def _get_bulk_action(self, value: str) -> Callable[[str], None] | None:
        return {
            "1": self._update_doi,
        }.get(value)

    def _update_doi(self, package_id: str) -> None:
        create_or_update_doi(package_id)


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
doi_dashboard.add_url_rule("/list", view_func=ApDoiView.as_view("list"))

doi_dashboard.add_url_rule(
    "/config",
    view_func=ApConfigurationPageView.as_view("config", "ap_doi_config"),
)
