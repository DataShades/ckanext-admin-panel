from __future__ import annotations

from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.ap_main.types as ap_types
from ckanext.ap_main.interfaces import IAdminPanel


collect_sections_signal = tk.signals.ckanext.signal(
    "ap_main:collect_config_sections",
    "Collect configuration section from subscribers",
)

collect_config_schemas_signal = tk.signals.ckanext.signal(
    "ap_main:collect_config_schemas",
    "Collect config schemas from subscribers",
)


def ap_before_request() -> None:
    """Check if user has access to the admin panel.

    Calls `admin_panel_access` auth function to check if user has access to the
    admin panel view. If you want to change the auth function logic, you can chain it.

    Raises:
        tk.NotAuthorized: If user does not have access to the admin panel

    Example:
        ```python
        from flask import Blueprint, Response

        from ckanext.ap_main.utils import ap_before_request

        blueprint = Blueprint("my_blueprint", __name__, url_prefix="/admin-panel/my_blueprint")
        blueprint.before_request(ap_before_request)
        ```
    """
    try:
        tk.check_access(
            "admin_panel_access",
            {"user": tk.current_user.name},
        )
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


def get_config_schema(schema_id: str) -> dict[Any, Any] | None:
    """Get a schema by its id from the loaded schemas.

    Args:
        schema_id: The id of the schema to get

    Returns:
        The schema if found, otherwise None
    """
    from ckanext.scheming.plugins import _expand_schemas, _load_schemas

    for _, schemas_paths in collect_config_schemas_signal.send():
        schemas = _load_schemas(schemas_paths, "schema_id")
        expanded_schemas = _expand_schemas(schemas)

        if schema := expanded_schemas.get(schema_id):
            return schema
