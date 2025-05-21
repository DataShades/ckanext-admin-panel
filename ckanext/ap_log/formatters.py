from __future__ import annotations

import logging
from typing import Callable

from ckanext.toolbelt.decorators import Collector

from ckanext.ap_main import types

get_formatters: Callable[[], dict[str, types.Formatter]]
formatter, get_formatters = Collector().split()


@formatter
def log_level(
    value: int,
    options: types.Options,
    column: types.ColumnDefinition,
    row: types.Row,
    table: types.TableDefinition,
) -> str:
    """Render a log level as a string.

    Args:
        value: numeric representation of logging level
        options: options for the renderer
        column: column definition
        row: row data
        table: table definition

    Returns:
        log level name
    """
    return logging.getLevelName(value)
