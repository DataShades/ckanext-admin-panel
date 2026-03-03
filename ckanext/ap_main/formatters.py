from __future__ import annotations

import ckan.model as model
from ckan.plugins import toolkit as tk
from ckanext.tables.shared import FormatterResult, Options, Value, formatters


class DateFormatter(formatters.BaseFormatter):
    """Render a datetime object as a string."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the date value.

        Options:
            - `date_format` (str) - date format string. **Default** is `%d/%m/%Y - %H:%M`
        """
        date_format: str = options.get("date_format", "%d/%m/%Y - %H:%M")
        return tk.h.render_datetime(value, date_format=date_format)


class UserLinkFormatter(formatters.BaseFormatter):
    """Generate a link to the user profile page with an avatar."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the user link.

        Options:
            - `maxlength` (int) - maximum length of the user name. **Default** is `20`
            - `avatar` (int) - size of the avatar. **Default** is `20`
        """
        if not value:
            return ""

        user = model.User.get(value)
        if not user:
            return value

        maxlength = options.get("maxlength") or 20
        avatar = options.get("avatar") or 20

        display_name = user.display_name
        if maxlength and len(user.display_name) > maxlength:
            display_name = display_name[:maxlength] + "..."

        return tk.h.literal(
            "{icon} {link}".format(
                icon=tk.h.snippet(
                    "user/snippets/placeholder.html",
                    size=avatar,
                    user_name=display_name,
                ),
                link=tk.h.link_to(
                    display_name, tk.h.url_for("user.read", id=user.name)
                ),
            )
        )


class BoolFormatter(formatters.BaseFormatter):
    """Render a boolean value as a string."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the boolean value."""
        return "Yes" if value else "No"


class ListFormatter(formatters.BaseFormatter):
    """Render a list as a comma-separated string."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the list value."""
        return ", ".join(value)


class NoneAsEmptyFormatter(formatters.BaseFormatter):
    """Render None as an empty string."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the value."""
        return value if value is not None else ""


class TrimStringFormatter(formatters.BaseFormatter):
    """Trim string to a certain length."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the string value.

        Options:
            - `max_length` (int) - maximum length of the string. **Default** is `79`
            - `add_ellipsis` (bool) - add ellipsis to the end of the string. **Default** is `True`
        """
        if not value:
            return ""

        max_length: int = options.get("max_length", 79)
        trimmed_value: str = str(value)[:max_length]

        if (
            tk.asbool(options.get("add_ellipsis", True))
            and len(str(value)) > max_length
        ):
            trimmed_value += "..."

        return trimmed_value


class ActionsFormatter(formatters.BaseFormatter):
    """Render actions for the table row."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the actions.

        Options:
            - `template` (str) - template to render the actions.
        """
        template = options.get("template", "admin_panel/tables/formatters/actions.html")

        # We need to access the table, column, and row which are passed in __call__ but not explicitly in format signature
        # BaseFormatter stores them in self.column, self.row, self.table_def during __call__
        # But looking at usage in other extensions, it seems we might need to rely on how tables calls it.
        # ckanext-tables BaseFormatter.format signature is (self, value: Value, options: Options) -> FormatterResult
        # But the old code used table, column, row.
        # In ckanext-tables, the formatter is instantiated per cell render or `__call__` sets context?
        # Actually in ckanext-tables shared/__init__.py, BaseFormatter.__call__ sets self.row, self.column etc before calling format.

        return tk.literal(
            tk.render(
                template,
                extra_vars={
                    "table": self.table_def,
                    "column": self.column,
                    "row": self.row,
                },
            )
        )


class JsonDisplayFormatter(formatters.BaseFormatter):
    """Render a JSON object as a string."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the JSON value."""
        return tk.literal(
            tk.render(
                "ap_cron/formatters/json.html",
                extra_vars={"value": value},
            )
        )


class ShortenPathFormatter(formatters.BaseFormatter):
    """Shorten a path to a certain length."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the path value.

        Options:
            - `max_length` (int) - maximum length of the path. **Default** is `50`
        """
        val_str = str(value)
        max_length: int = options.get("max_length", 50)

        if len(val_str) <= max_length:
            return val_str

        half = (max_length - 3) // 2
        return val_str[:half] + "..." + val_str[-half:]
