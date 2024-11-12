from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable

import ckan.model as model
from ckan.plugins import toolkit as tk
from ckanext.collection.types import BaseSerializer

from ckanext.toolbelt.decorators import Collector

from ckanext.ap_main.types import ColRenderer

renderer: Collector[ColRenderer]
get_renderers: Callable[[], dict[str, ColRenderer]]
renderer, get_renderers = Collector().split()


@renderer
def date(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")

    return tk.h.render_datetime(value, date_format=date_format)


@renderer
def user_link(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    """Generate a link to the user profile page with an avatar.

    It's a custom implementation of the linked_user
    function, where we replace an actual user avatar with a placeholder.

    Fetching an avatar requires an additional user_show call, and it's too
    expensive to do it for every user in the list. So we use a placeholder

    Args:
        value (str): user ID
        options (dict[str, Any]): options for the renderer
        name (str): column name
        record (Any): row data
        self (BaseSerializer): serializer instance
    """
    if not value:
        return ""

    user = model.User.get(value)

    if not user:
        return value

    maxlength = options.get("maxlength") or 20
    avatar = options.get("maxlength") or 20

    display_name = user.display_name

    if maxlength and len(user.display_name) > maxlength:
        display_name = display_name[:maxlength] + "..."

    return tk.h.literal(
        "{icon} {link}".format(
            icon=tk.h.snippet(
                "user/snippets/placeholder.html", size=avatar, user_name=display_name
            ),
            link=tk.h.link_to(display_name, tk.h.url_for("user.read", id=user.name)),
        )
    )


@renderer
def bool(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    return "Yes" if value else "No"


@renderer
def log_level(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    return logging.getLevelName(value)


@renderer
def list(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
):
    return ", ".join(value)


@renderer
def none_as_empty(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> Any:
    return value if value is not None else ""


@renderer
def day_passed(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    if not value:
        return "0"

    try:
        datetime_obj = datetime.fromisoformat(value)
    except AttributeError:
        return "0"

    current_date = datetime.now()

    days_passed = (current_date - datetime_obj).days

    return tk.literal(
        tk.render(
            "admin_panel/renderers/day_passed.html",
            extra_vars={"value": days_passed},
        )
    )


@renderer
def trim_string(
    value: str, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    """Trim string to a certain length"""
    if not value:
        return ""

    max_length: int = options.get("max_length", 79)
    trimmed_value: str = value[:max_length]

    if tk.asbool(options.get("add_ellipsis", True)):
        trimmed_value += "..."

    return trimmed_value
