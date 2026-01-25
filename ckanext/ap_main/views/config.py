from __future__ import annotations

from flask import Blueprint

import ckan.plugins.toolkit as tk

from ckanext.ap_main.utils import ap_before_request

ap_config_list = Blueprint("ap_config_list", __name__, url_prefix="/admin-panel")
ap_config_list.before_request(ap_before_request)


@ap_config_list.route("/config")
def index() -> str:
    return tk.render("admin_panel/config/config_list.html", extra_vars={})
