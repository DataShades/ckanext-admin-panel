from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.editable_config.shared import value_as_string

from ckanext.ap_main.utils import ap_before_request, get_config_schema
from ckanext.ap_main.views.generics import ApConfigurationPageView

log = logging.getLogger(__name__)
ap_example = Blueprint("ap_example", __name__, url_prefix="/admin-panel/example")
ap_example.before_request(ap_before_request)


class ApConfigurationDisplayPageView(MethodView):
    def get(self):
        self.schema = get_config_schema("admin_panel_example_config")
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


ap_example.add_url_rule(
    "/config",
    view_func=ApConfigurationPageView.as_view("config", "admin_panel_example_config"),
)

ap_example.add_url_rule(
    "/config_display",
    view_func=ApConfigurationDisplayPageView.as_view("display"),
)

blueprints = [ap_example]
