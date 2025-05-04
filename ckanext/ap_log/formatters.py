from __future__ import annotations

import logging
from typing import Any

from ckanext.toolbelt.decorators import Collector

from ckanext.ap_main.table import TableDefinition

renderer, get_formatters = Collector().split()


@renderer
def log_level(
    value: Any, options: dict[str, Any], name: str, record: Any, table: TableDefinition
) -> str:
    return logging.getLevelName(value)
