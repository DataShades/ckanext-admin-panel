from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector

from ckanext.ap_main.table import TableDefinition

renderer, get_formatters = Collector("ap_support").split()


@renderer
def status(
    value: Any, options: dict[str, Any], name: str, record: Any, table: TableDefinition
) -> str:
    return tk.literal(
        tk.render(
            "ap_support/renderers/status.html",
            extra_vars={"value": value},
        )
    )
