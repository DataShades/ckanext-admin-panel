from __future__ import annotations

from typing import Callable

import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector

import ckanext.ap_main.types as types
from ckanext.ap_main.types import Formatter

get_formatters: Callable[[], dict[str, Formatter]]
formatter, get_formatters = Collector().split()


@formatter
def last_run(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")

    if not value:
        return tk._("Never")

    return tk.h.render_datetime(value, date_format=date_format)


@formatter
def schedule(
    value: types.Value,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> types.FormatterResult:
    tooltip = tk.h.ap_cron_explain_cron_schedule(value)

    return tk.literal(
        tk.render(
            "ap_cron/tables/formatters/schedule.html",
            extra_vars={"value": value, "tooltip": tooltip},
        )
    )
