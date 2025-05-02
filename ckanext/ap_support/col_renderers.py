from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk

from ckanext.collection.types import BaseSerializer
from ckanext.toolbelt.decorators import Collector

renderer, get_renderers = Collector("ap_support").split()


@renderer
def status(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    return tk.literal(
        tk.render(
            "ap_support/renderers/status.html",
            extra_vars={"value": value},
        )
    )
