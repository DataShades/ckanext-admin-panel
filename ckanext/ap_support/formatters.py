from __future__ import annotations

from datetime import datetime

import ckan.plugins.toolkit as tk
from ckanext.tables.shared import FormatterResult, Options, Value, formatters


class StatusFormatter(formatters.BaseFormatter):
    """Formatter for the status column."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the status value."""
        return tk.literal(
            tk.render(
                "tables/formatters/status.html",
                extra_vars={"value": value},
            )
        )

class DayPassedFormatter(formatters.BaseFormatter):
    """Calculate the number of days passed since the date."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the date value as days passed."""
        if not value:
            return "0"

        try:
            datetime_obj = datetime.fromisoformat(str(value))
        except (AttributeError, ValueError):
            # Try to handle if value is already a datetime object
            if isinstance(value, datetime):
                datetime_obj = value
            else:
                return "0"

        current_date = datetime.now()
        days_passed = (current_date - datetime_obj).days

        return tk.literal(
            tk.render(
                "tables/formatters/day_passed.html",
                extra_vars={"value": days_passed},
            )
        )
