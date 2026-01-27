from __future__ import annotations

from typing import Any

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.lib.navl.dictization_functions as dict_fns
import ckan.plugins.toolkit as tk
from ckan import logic, model
from ckan.lib import app_globals
from ckan.logic.schema import update_configuration_schema
from ckan.views.home import CACHE_PARAMETERS

import ckanext.ap_main.utils as ap_utils

ap_basic = Blueprint("ap_basic", __name__, url_prefix="/admin-panel")
ap_basic.before_request(ap_utils.ap_before_request)


class ResetView(MethodView):
    def get(self) -> str | Response:
        if "cancel" in tk.request.args:
            return tk.redirect_to("ap_basic.config")
        return tk.render("admin_panel/config/confirm_reset.html")

    def post(self) -> Response:
        for item in self._get_config_items():
            model.delete_system_info(item)

        app_globals.reset()
        return tk.redirect_to("ap_basic.config")

    def _get_config_items(self) -> list[str]:
        return [
            "ckan.site_title",
            "ckan.theme",
            "ckan.site_description",
            "ckan.site_logo",
            "ckan.site_about",
            "ckan.site_intro_text",
            "ckan.site_custom_css",
            "ckan.homepage_style",
        ]


class ConfigView(MethodView):
    def get(self) -> str:
        return tk.render(
            "admin_panel/config/basic.html",
            extra_vars=dict(
                data={key: tk.config.get(key) for key in update_configuration_schema()},
                errors={},
                **self._get_config_options(),
            ),
        )

    def post(self) -> str | Response:
        try:
            req: dict[str, Any] = tk.request.form.copy()
            req.update(tk.request.files.to_dict())
            data_dict = logic.clean_dict(
                dict_fns.unflatten(
                    logic.tuplize_dict(
                        logic.parse_params(req, ignore_keys=CACHE_PARAMETERS)
                    )
                )
            )

            del data_dict["save"]
            tk.get_action("config_option_update")(
                {"user": tk.current_user.name}, data_dict
            )

        except tk.ValidationError as e:
            items = self._get_config_options()
            vars = dict(
                data=tk.request.form,
                errors=e.error_dict,
                error_summary=e.error_summary,
                form_items=items,
                **items,
            )
            return tk.render("admin_panel/config/basic.html", extra_vars=vars)

        tk.h.flash_success(tk._("Settings have been saved"))

        return tk.redirect_to("ap_basic.config")

    def _get_config_options(self) -> dict[str, list[dict[str, str]]]:
        return {
            "homepages": [
                {
                    "value": "1",
                    "text": (
                        "Introductory area, search, featured"
                        " group and featured organization"
                    ),
                },
                {
                    "value": "2",
                    "text": (
                        "Search, stats, introductory area, "
                        "featured organization and featured group"
                    ),
                },
                {"value": "3", "text": "Search, introductory area and stats"},
            ]
        }


class EditableConfigView(MethodView):
    """Adapter for ckanext-editable-config.

    Once this extension get stable API, remove this logic and implement proper
    hooks inside ckanext-editable-config.

    """

    def _render(
        self,
        data: dict[str, Any] | None = None,
        error: tk.ValidationError | None = None,
    ):
        """Shared method for normal GET and failed POST request."""
        options = tk.get_action("editable_config_list")({}, {})

        extra_vars: dict[str, Any] = {
            "data": data or {},
            "options": options,
            "errors": error.error_dict if error else None,
            "error_summary": error.error_summary if error else None,
        }

        return tk.render("admin_panel/config/editable_config.html", extra_vars)

    def get(self) -> str:
        return self._render()

    def post(self) -> str | Response:
        data = logic.parse_params(tk.request.form)

        change: dict[str, Any] = {}
        reset: list[str] = []

        for key in data:
            if key.startswith("reset:"):
                # remove any customization from option if Reset checkbox is
                # checked.
                clean_key = key[6:]
                change.pop(clean_key, None)
                reset.append(clean_key)

            else:
                if key in reset:
                    # don't try to modify options that will be removed. It
                    # won't change the result. This condition exists merely for
                    # optimization
                    continue
                change[key] = data[key]

        try:
            tk.get_action("editable_config_update")(
                {},
                {"change": change, "reset": reset},
            )
        except tk.ValidationError as e:
            return self._render(data, e)

        tk.h.flash_success(tk._("Settings have been saved"))
        return tk.redirect_to("ap_basic.editable_config")


ap_basic.add_url_rule("/config/basic", view_func=ConfigView.as_view("config"))
ap_basic.add_url_rule(
    "/config/editable-config", view_func=EditableConfigView.as_view("editable_config")
)
ap_basic.add_url_rule("/config/basic/reset", view_func=ResetView.as_view("reset"))
