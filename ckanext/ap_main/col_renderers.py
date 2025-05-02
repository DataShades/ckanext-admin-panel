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
    value: datetime,
    options: dict[str, Any],
    name: str,
    record: Any,
    self: BaseSerializer,
) -> str:
    """Render a datetime object as a string.

    Args:
        value (datetime): date value
        options (dict[str, Any]): options for the renderer
        name (str): column name
        record (Any): row data
        self (BaseSerializer): serializer instance

    Options:
        - `date_format` (str) - date format string. **Default** is `%d/%m/%Y - %H:%M`

    Returns:
        formatted date
    """
    date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")

    return tk.h.render_datetime(value, date_format=date_format)


@renderer
def user_link(
    value: str, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
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

    Options:
        - `maxlength` (int) - maximum length of the user name. **Default** is `20`
        - `avatar` (int) - size of the avatar. **Default** is `20`

    Returns:
        User link with an avatar placeholder
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
    """Render a boolean value as a string.

    Args:
        value (Any): boolean value
        options (dict[str, Any]): options for the renderer
        name (str): column name
        record (Any): row data
        self (BaseSerializer): serializer instance

    Returns:
        "Yes" if value is True, otherwise "No"
    """
    return "Yes" if value else "No"


@renderer
def log_level(
    value: int, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    """Render a log level as a string.

    Args:
        value (Any): numeric representation of logging level
        options (dict[str, Any]): options for the renderer
        name (str): column name
        record (Any): row data
        self (BaseSerializer): serializer instance

    Returns:
        log level name
    """
    return logging.getLevelName(value)


@renderer
def list(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    """Render a list as a comma-separated string.

    Args:
        value (Any): list value
        options (dict[str, Any]): options for the renderer
        name (str): column name
        record (Any): row data
        self (BaseSerializer): serializer instance

    Returns:
        comma-separated string
    """
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
    """Calculate the number of days passed since the date.

    Args:
        value (Any): date value
        options (dict[str, Any]): options for the renderer
        name (str): column name
        record (Any): row data
        self (BaseSerializer): serializer instance

    Returns:
        A priority badge with day counter and color based on priority.
    """
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
    """Trim string to a certain length.

    Args:
        value (str): string value
        options (dict[str, Any]): options for the renderer
        name (str): column name
        record (Any): row data
        self (BaseSerializer): serializer instance

    Options:
        - `max_length` (int) - maximum length of the string. **Default** is `79`
        - `add_ellipsis` (bool) - add ellipsis to the end of the string. **Default** is `True`

    Returns:
        trimmed string
    """
    if not value:
        return ""

    max_length: int = options.get("max_length", 79)
    trimmed_value: str = value[:max_length]

    if tk.asbool(options.get("add_ellipsis", True)):
        trimmed_value += "..."

    return trimmed_value
