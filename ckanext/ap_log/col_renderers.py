from __future__ import annotations

import logging
from typing import Any, Callable

from ckanext.collection.types import BaseSerializer
from ckanext.toolbelt.decorators import Collector

from ckanext.ap_main.types import ColRenderer

renderer: Collector[ColRenderer]
get_renderers: Callable[[], dict[str, ColRenderer]]
renderer, get_renderers = Collector().split()


@renderer
def log_level(
    value: Any, options: dict[str, Any], name: str, record: Any, self: BaseSerializer
) -> str:
    return logging.getLevelName(value)
