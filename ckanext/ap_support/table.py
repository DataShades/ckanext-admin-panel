from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import aliased

import ckan.plugins.toolkit as tk
from ckan import model as ckan_model

import ckanext.tables.shared as t
from ckanext.ap_support import formatters as sf
from ckanext.ap_support.model import Ticket


def _build_support_tickets_stmt():
    """Build the stmt for the support tickets table.

    We join the CKAN User table twice (author + assignee) and expose
    COALESCE(fullname, name) as ``author_name`` / ``assignee_name`` so
    that column header filters operate on human-readable names rather
    than raw UUIDs.  The raw ID columns are included as hidden columns
    so that formatters can still build profile links.

    Datetime columns are pre-formatted as ISO-style strings
    (``YYYY-MM-DD HH24:MI``) so they sort correctly as plain strings
    and can be filtered without a custom formatter.
    """
    author_alias = aliased(ckan_model.User, name="author")
    assignee_alias = aliased(ckan_model.User, name="assignee")

    author_display = func.coalesce(author_alias.fullname, author_alias.name).label(
        "author_name"
    )
    assignee_display = func.coalesce(
        assignee_alias.fullname, assignee_alias.name
    ).label("assignee_name")

    return (
        select(
            Ticket.id,
            Ticket.subject,
            Ticket.status,
            Ticket.category,
            func.to_char(Ticket.created_at, "YYYY-MM-DD HH24:MI").label("created_at"),
            func.to_char(Ticket.updated_at, "YYYY-MM-DD HH24:MI").label("updated_at"),
            Ticket.author_id,
            Ticket.assignee_id,
            author_display,
            assignee_display,
        )
        .outerjoin(author_alias, Ticket.author_id == author_alias.id)
        .outerjoin(assignee_alias, Ticket.assignee_id == assignee_alias.id)
        .order_by(Ticket.updated_at.desc())
    )


class SupportTable(t.TableDefinition):
    def __init__(self):
        super().__init__(
            name="support_tickets",
            table_template="ap_support/list.html",
            data_source=t.DatabaseDataSource(stmt=_build_support_tickets_stmt()),
            columns=[
                t.ColumnDefinition(field="subject"),
                t.ColumnDefinition(
                    field="status",
                    formatters=[(sf.StatusFormatter, {})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(
                    field="author_name",
                    title="Author",
                    formatters=[(sf.UserNameLinkFormatter, {"id_field": "author_id"})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(
                    field="assignee_name",
                    title="Assignee",
                    formatters=[
                        (sf.UserNameLinkFormatter, {"id_field": "assignee_id"})
                    ],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(field="category", title="Category"),
                t.ColumnDefinition(field="created_at", title="Created At"),
                t.ColumnDefinition(field="updated_at", title="Updated At"),
            ],
            row_actions=[
                t.RowActionDefinition(
                    action="view",
                    label="View",
                    icon="fa fa-eye",
                    callback=lambda row: t.ActionHandlerResult(
                        success=True,
                        redirect=tk.url_for(
                            "ap_support.ticket_read", ticket_id=row["id"]
                        ),
                    ),
                ),
                t.RowActionDefinition(
                    action="delete",
                    label="Delete",
                    icon="fa fa-trash",
                    callback=self.row_action_delete,
                    with_confirmation=True,
                ),
            ],
            bulk_actions=[
                t.BulkActionDefinition(
                    action="close_tickets",
                    label="Close selected tickets",
                    icon="fa fa-check",
                    callback=self.bulk_close,
                ),
                t.BulkActionDefinition(
                    action="reopen_tickets",
                    label="Reopen selected tickets",
                    icon="fa fa-folder-open",
                    callback=self.bulk_reopen,
                ),
                t.BulkActionDefinition(
                    action="remove_tickets",
                    label="Remove selected tickets",
                    icon="fa fa-trash",
                    callback=self.bulk_remove,
                ),
            ],
        )

    def row_action_delete(self, row: t.Row) -> t.ActionHandlerResult:
        try:
            tk.get_action("ap_support_ticket_delete")(
                {"ignore_auth": True}, {"id": row["id"]}
            )
        except tk.ValidationError:
            return t.ActionHandlerResult(
                success=False, error=tk._("Error deleting ticket.")
            )

        return t.ActionHandlerResult(success=True)

    def bulk_close(self, rows: list[t.Row]) -> t.ActionHandlerResult:
        for row in rows:
            tk.get_action("ap_support_ticket_update")(
                {"ignore_auth": True},
                {"id": row["id"], "status": Ticket.Status.closed},
            )
        return t.ActionHandlerResult(success=True, message="Ticket(s) closed.")

    def bulk_reopen(self, rows: list[t.Row]) -> t.ActionHandlerResult:
        for row in rows:
            tk.get_action("ap_support_ticket_update")(
                {"ignore_auth": True},
                {"id": row["id"], "status": Ticket.Status.opened},
            )
        return t.ActionHandlerResult(success=True, message="Ticket(s) reopened.")

    def bulk_remove(self, rows: list[t.Row]) -> t.ActionHandlerResult:
        for row in rows:
            tk.get_action("ap_support_ticket_delete")(
                {"ignore_auth": True}, {"id": row["id"]}
            )
        return t.ActionHandlerResult(success=True, message="Ticket(s) removed.")


class UserTicketTable(t.TableDefinition):
    """Table for displaying tickets created by the current user."""

    def __init__(self):
        user_id = tk.g.userobj.id if tk.g.userobj else None

        if not user_id:
            tk.abort(404, tk._("User not found"))

        stmt = (
            select(
                Ticket.id,
                Ticket.subject,
                Ticket.status,
                Ticket.category,
                func.to_char(Ticket.created_at, "YYYY-MM-DD HH24:MI").label(
                    "created_at"
                ),
                func.to_char(Ticket.updated_at, "YYYY-MM-DD HH24:MI").label(
                    "updated_at"
                ),
            )
            .where(Ticket.author_id == user_id)
            .order_by(Ticket.updated_at.desc())
        )

        super().__init__(
            name="my_support_tickets",
            table_template="ap_support/my_tickets.html",
            data_source=t.DatabaseDataSource(stmt=stmt),
            columns=[
                t.ColumnDefinition(field="subject"),
                t.ColumnDefinition(
                    field="status",
                    formatters=[(sf.StatusFormatter, {})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(field="category", title="Category"),
                t.ColumnDefinition(field="created_at", title="Created At"),
                t.ColumnDefinition(field="updated_at", title="Updated At"),
            ],
            row_actions=[
                t.RowActionDefinition(
                    action="view",
                    label="View",
                    icon="fa fa-eye",
                    callback=lambda row: t.ActionHandlerResult(
                        success=True,
                        redirect=tk.url_for(
                            "ap_support.ticket_read", ticket_id=row["id"]
                        ),
                    ),
                ),
            ],
        )
