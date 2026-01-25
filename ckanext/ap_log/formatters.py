from __future__ import annotations

import logging
from ckanext.tables.shared import FormatterResult, Options, Value, formatters


class LogLevelFormatter(formatters.BaseFormatter):
    """Render a log level as a string."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the log level value."""
        return logging.getLevelName(int(value))
