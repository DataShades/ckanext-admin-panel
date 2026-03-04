from __future__ import annotations


import ckan.plugins.toolkit as tk
from ckan import model

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


class UserNameLinkFormatter(formatters.BaseFormatter):
    """Render an avatar + profile link for a user.

    Unlike :class:`~ckanext.ap_main.formatters.UserLinkFormatter`, the
    ``value`` here is already the human-readable display name (resolved by
    the SQL query via ``COALESCE(fullname, name)``), so the column can be
    made filterable without confusing users with UUID searches.

    The actual user UUID is read from the same row under the key specified by
    the ``id_field`` option (e.g. ``"author_id"``), which is used to look up
    the user record for URL-building.

    Options:
        - ``id_field`` (str) – Row key that holds the user UUID.
          **Required.**
        - ``maxlength`` (int) – Clip display name to this length. Default 20.
        - ``avatar`` (int) – Avatar placeholder size in pixels. Default 20.
    """

    def format(self, value: Value, options: Options) -> FormatterResult:
        if not value:
            return ""

        id_field = options.get("id_field")
        user_id = self.initial_row.get(id_field) if id_field else None
        user = model.User.get(user_id) if user_id else None

        maxlength: int = options.get("maxlength") or 20
        avatar: int = options.get("avatar") or 20

        display_name = str(value)
        if len(display_name) > maxlength:
            display_name = display_name[:maxlength] + "..."

        icon = tk.h.snippet(
            "user/snippets/placeholder.html",
            size=avatar,
            user_name=display_name,
        )

        link = (
            tk.h.link_to(display_name, tk.h.url_for("user.read", id=user.name))
            if user
            else display_name
        )

        return tk.h.literal(f"{icon} {link}")
