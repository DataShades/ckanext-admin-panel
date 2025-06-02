from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import ckan.model as model
from ckan.plugins import toolkit as tk

from ckanext.toolbelt.decorators import Collector

import ckanext.ap_main.types as types
from ckanext.ap_main.table import TableDefinition

get_formatters: Callable[[], dict[str, types.Formatter]]
formatter, get_formatters = Collector().split()


@formatter
def date(
    value: datetime,
    options: dict[str, Any],
    name: str,
    record: Any,
    table: TableDefinition,
) -> str:
    """Render a datetime object as a string.

    Args:
        value (datetime): date value
        options: options for the renderer
        name (str): column name
        record (Any): row data
        table: table definition

    Options:
        - `date_format` (str) - date format string. **Default** is `%d/%m/%Y - %H:%M`

    Returns:
        formatted date
    """
    date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")

    return tk.h.render_datetime(value, date_format=date_format)


@formatter
def user_link(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    """Generate a link to the user profile page with an avatar.

    It's a custom implementation of the linked_user
    function, where we replace an actual user avatar with a placeholder.

    Fetching an avatar requires an additional user_show call, and it's too
    expensive to do it for every user in the list. So we use a placeholder

    Args:
        value (str): user ID
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition

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


@formatter
def bool(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    """Render a boolean value as a string.

    Args:
        value (Any): boolean value
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition
    Returns:
        "Yes" if value is True, otherwise "No"
    """
    return "Yes" if value else "No"


@formatter
def list(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    """Render a list as a comma-separated string.

    Args:
        value: list value
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition

    Returns:
        comma-separated string
    """
    return ", ".join(value)


@formatter
def none_as_empty(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    return value if value is not None else ""


@formatter
def day_passed(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    """Calculate the number of days passed since the date.

    Args:
        value: date value
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition
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
            "admin_panel/tables/formatters/day_passed.html",
            extra_vars={"value": days_passed},
        )
    )


@formatter
def trim_string(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    """Trim string to a certain length.

    Args:
        value: string value
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition

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


@formatter
def actions(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    """Render actions for the table row.

    Args:
        value: string value
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition

    Options:
        - `template` (str) - template to render the actions.
    """

    template = options.get("template", "admin_panel/tables/formatters/actions.html")

    return tk.literal(
        tk.render(
            template,
            extra_vars={"table": table, "column": column, "row": row},
        )
    )


@formatter
def json_display(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    """Render a JSON object as a string.

    Args:
        value: JSON object
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition

    Returns:
        JSON object as a string
    """
    return tk.literal(
        tk.render(
            "ap_cron/formatters/json.html",
            extra_vars={"value": value},
        )
    )


@formatter
def shorten_path(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    """Shorten a path to a certain length.

    Args:
        value: path value
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition

    Options:
        - `max_length` (int) - maximum length of the path. **Default** is `50`

    Returns:
        shortened path
    """
    max_length: int = options.get("max_length", 50)

    if len(value) <= max_length:
        return value

    half = (max_length - 3) // 2
    return value[:half] + "..." + value[-half:]
