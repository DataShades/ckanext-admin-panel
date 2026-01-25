from __future__ import annotations

import ckan.plugins.toolkit as tk
from ckanext.tables.shared import FormatterResult, Options, Value, formatters


class LastRunFormatter(formatters.BaseFormatter):
    """Formatter for the last run data."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")

        if not value:
            return tk._("Never")

        return tk.h.render_datetime(value, date_format=date_format)


class ScheduleFormatter(formatters.BaseFormatter):
    """Formatter for the cron schedule."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        tooltip = tk.h.ap_cron_explain_cron_schedule(value)

        return tk.literal(
            tk.render(
                "ap_cron/tables/formatters/schedule.html",
                extra_vars={"value": value, "tooltip": tooltip},
            )
        )
