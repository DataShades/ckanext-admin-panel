from __future__ import annotations

from typing import Any, Callable

import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector

from ckanext.ap_main.table import TableDefinition
from ckanext.ap_main.types import Formatter

get_formatters: Callable[[], dict[str, Formatter]]
formatter, get_formatters = Collector().split()


@formatter
def last_run(
    value: Any, options: dict[str, Any], name: str, record: Any, table: TableDefinition
) -> str:
    date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")

    if not value:
        return tk._("Never")

    return tk.h.render_datetime(value, date_format=date_format)


@formatter
def schedule(
    value: Any, options: dict[str, Any], name: str, record: Any, table: TableDefinition
) -> str:
    tooltip = tk.h.ap_cron_explain_cron_schedule(value)

    return tk.literal(
        tk.render(
            "ap_cron/formatters/schedule.html",
            extra_vars={"value": value, "tooltip": tooltip},
        )
    )


@formatter
def json_display(
    value: Any, options: dict[str, Any], name: str, record: Any, table: TableDefinition
) -> str:
    return tk.literal(
        tk.render(
            "ap_cron/formatters/json.html",
            extra_vars={"value": value},
        )
    )
