from __future__ import annotations

import ckan.plugins.toolkit as tk
from ckanext.tables.shared import FormatterResult, Options, Value, formatters


class StatusFormatter(formatters.BaseFormatter):
    """Formatter for the status column."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the status value."""
        return tk.literal(
            tk.render(
                "ap_support/renderers/status.html",
                extra_vars={"value": value},
            )
        )
