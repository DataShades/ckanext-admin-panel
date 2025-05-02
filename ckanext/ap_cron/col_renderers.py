from __future__ import annotations

from typing import Any, Callable

import ckan.plugins.toolkit as tk

from ckanext.collection.types import BaseSerializer
from ckanext.toolbelt.decorators import Collector

from ckanext.ap_main.types import ColRenderer

renderer: Collector[ColRenderer]
get_renderers: Callable[[], dict[str, ColRenderer]]
renderer, get_renderers = Collector().split()


@renderer
def last_run(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")

    if not value:
        return tk._("Never")

    return tk.h.render_datetime(value, date_format=date_format)


@renderer
def schedule(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    tooltip = tk.h.ap_cron_explain_cron_schedule(value)

    return tk.literal(
        tk.render(
            "ap_cron/renderers/schedule.html",
            extra_vars={"value": value, "tooltip": tooltip},
        )
    )


@renderer
def json_display(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    return tk.literal(
        tk.render(
            "ap_cron/renderers/json.html",
            extra_vars={"value": value},
        )
    )
