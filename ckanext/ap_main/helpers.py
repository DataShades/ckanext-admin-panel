from __future__ import annotations

import json
from typing import Any

import ckan.lib.munge as munge
import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector
from ckanext.toolbelt.utils.cache import Cache

import ckanext.ap_main.config as ap_config
import ckanext.ap_main.utils as ap_utils
from ckanext.ap_main.interfaces import IAdminPanel
from ckanext.ap_main.types import SectionConfig, ToolbarButton, Formatter

helper, get_helpers = Collector("ap").split()
_formatter_cache: dict[str, Formatter] = {}


@helper
def get_all_formatters() -> dict[str, Formatter]:
    """Get all registered tabulator formatters.

    A formatter is a function that takes a column value and can modify its appearance
    in a table.

    Returns:
        A mapping of formatter names to formatter functions
    """
    if not _formatter_cache:
        for plugin in reversed(list(p.PluginImplementations(IAdminPanel))):
            for name, fn in plugin.get_formatters().items():
                _formatter_cache[name] = fn

    return _formatter_cache


@helper
def get_config_sections() -> list[SectionConfig]:
    """Prepare a config section structure for render.

    Returns:
        A list of sections with their config items
    """
    config_sections = {}

    for _, section in ap_utils.collect_sections_signal.send():
        config_sections.setdefault(
            section["name"], {"name": section["name"], "configs": []}
        )
        config_sections[section["name"]]["configs"].extend(section["configs"])

    sections = list(config_sections.values())
    sections.sort(key=lambda x: x["name"])

    return sections


@helper
@Cache(duration=900)  # cache for 15 minutes
def get_toolbar_structure() -> list[ToolbarButton]:
    """Prepare a toolbar structure for render.

    An extension can register its own toolbar buttons by implementing the
    `register_toolbar_button` method in the `IAdminPanel` interface.

    Returns:
        A list of toolbar button objects
    """
    configuration_subitems = [
        ToolbarButton(
            label=section["name"],
            subitems=[
                ToolbarButton(
                    label=config_item["name"], url=tk.url_for(config_item["blueprint"])
                )
                for config_item in section["configs"]
            ],
        )
        for section in get_config_sections()
    ]

    default_structure = [
        ToolbarButton(
            label=tk._("Content"),
            icon="fa fa-folder",
            url=tk.url_for("ap_content.list"),
        ),
        ToolbarButton(
            label=tk._("Configuration"),
            icon="fa fa-gear",
            url=tk.url_for("ap_config_list.index"),
            subitems=configuration_subitems,
        ),
        ToolbarButton(
            label=tk._("Users"),
            icon="fa fa-user-friends",
            url=tk.url_for("ap_user.list"),
            subitems=[
                ToolbarButton(
                    label=tk._("Add user"),
                    url=tk.url_for("ap_user.create"),
                    icon="fa fa-user-plus",
                )
            ],
        ),
        ToolbarButton(
            label=tk._("Reports"),
            icon="fa fa-chart-bar",
            subitems=[],
        ),
        ToolbarButton(
            icon="fa fa-user",
            url=tk.url_for("user.read", id=tk.current_user.name),
            label=tk.current_user.display_name,
            attributes={"title": tk._("View profile"), "class": "ms-lg-auto"},
        ),
        ToolbarButton(
            icon="fa fa-gavel",
            url=tk.url_for("admin.index"),
            aria_label=tk._("Old admin"),
            attributes={"title": tk._("Old admin")},
        ),
        ToolbarButton(
            icon="fa fa-tachometer",
            url=tk.url_for("dashboard.datasets"),
            aria_label=tk._("View dashboard"),
            attributes={"title": tk._("View dashboard")},
        ),
        ToolbarButton(
            icon="fa fa-cog",
            url=tk.url_for("user.edit", id=tk.current_user.name),
            aria_label=tk._("Profile settings"),
            attributes={"title": tk._("Profile settings")},
        ),
    ]

    if tk.h.ap_show_toolbar_theme_switcher():
        default_structure.append(
            ToolbarButton(
                icon="fa-solid fa-moon",
                aria_label=tk._("Theme Switcher"),
                url="#",
                attributes={
                    "title": tk._("Theme Switcher"),
                    "data-module": "ap-theme-switcher",
                    "class": "ap-theme-switcher",
                },
            ),
        )

    # place logout button at the end
    default_structure.append(
        ToolbarButton(
            icon="fa fa-sign-out",
            url=tk.url_for("user.logout"),
            aria_label=tk._("Log out"),
            attributes={"title": tk._("Log out")},
        )
    )

    for plugin in reversed(list(p.PluginImplementations(IAdminPanel))):
        default_structure = plugin.register_toolbar_button(default_structure)

    return default_structure


@helper
def munge_string(value: str) -> str:
    """Munge a string using CKAN's munge_name function.

    Args:
        value: The string to munge

    Returns:
        The munged string
    """
    return munge.munge_name(value)


@helper
def show_toolbar_theme_switcher() -> bool:
    """Check if the toolbar theme switcher should be displayed."""
    return ap_config.show_toolbar_theme_switcher()


@helper
def user_add_role_options() -> list[dict[str, str | int]]:
    """Return a list of options for a user add form.

    Returns:
        A list of options for a user add form
    """
    return [
        {"value": "user", "text": "Regular user"},
        {"value": "sysadmin", "text": "Sysadmin"},
    ]


@helper
def generate_page_unique_class() -> str:
    """Build a unique css class for each page.

    Returns:
        A unique css class for the current page
    """

    return tk.h.ap_munge_string((f"ap-{tk.request.endpoint}"))


@helper
def calculate_priority(value: int, threshold: int) -> str:
    """Calculate the priority of a value based on a threshold.

    Args:
        value: The value to calculate the priority for
        threshold: The threshold to compare the value to

    Returns:
        The priority of the value

    Example:
        ```python
        from ckanext.ap_main.helpers import calculate_priority

        priority = calculate_priority(10, 100)
        print(priority) # low
        ```
    """
    percentage = value / threshold * 100

    if percentage < 25:
        return "low"
    elif percentage < 50:
        return "medium"
    elif percentage < 75:
        return "high"
    else:
        return "urgent"


@helper
def build_url_from_params(
    endpoint: str, url_params: dict[str, Any], row: dict[str, Any]
) -> str:
    """Build an action URL based on the endpoint and URL parameters.

    The url_params might contain values like $id, $type, etc.
    We need to replace them with the actual values from the row

    Args:
        endpoint: The endpoint to build the URL for
        url_params: The URL parameters to build the URL for
        row: The row to build the URL for
    """
    params = url_params.copy()

    for key, value in params.items():
        if value.startswith("$"):
            params[key] = row[value[1:]]

    return tk.url_for(endpoint, **params)


@helper
def dumps(value: Any) -> str:
    """Convert a value to a JSON string.

    Args:
        value: The value to convert to a JSON string

    Returns:
        The JSON string
    """
    return json.dumps(value)
