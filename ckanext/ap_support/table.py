from __future__ import annotations

from sqlalchemy import select

import ckan.plugins.toolkit as tk

import ckanext.tables.shared as t
from ckanext.ap_main import formatters as f
from ckanext.ap_support import formatters as sf
from ckanext.ap_support.model import Ticket


class SupportTable(t.TableDefinition):
    def __init__(self):
        super().__init__(
            name="support_tickets",
            table_template="ap_support/list.html",
            data_source=t.DatabaseDataSource(
                stmt=select(
                    Ticket.id,
                    Ticket.subject,
                    Ticket.status,
                    Ticket.category,
                    Ticket.created_at,
                    Ticket.updated_at,
                    Ticket.author_id,
                    Ticket.assignee_id,
                ).order_by(Ticket.updated_at.desc()),
            ),
            columns=[
                t.ColumnDefinition(field="subject"),
                t.ColumnDefinition(
                    field="status",
                    formatters=[(sf.StatusFormatter, {})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(
                    field="author_id",
                    title="Author",
                    formatters=[(f.UserLinkFormatter, {})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(
                    field="assignee_id",
                    title="Assignee",
                    formatters=[(f.UserLinkFormatter, {})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(field="category", title="Category"),
                t.ColumnDefinition(
                    field="created_at",
                    title="Created N days ago",
                    formatters=[(sf.DayPassedFormatter, {})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(
                    field="updated_at",
                    formatters=[(f.DateFormatter, {})],
                ),
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
                Ticket.created_at,
                Ticket.updated_at,
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
                t.ColumnDefinition(
                    field="created_at",
                    title="Created N days ago",
                    formatters=[(sf.DayPassedFormatter, {})],
                    tabulator_formatter="html",
                ),
                t.ColumnDefinition(
                    field="updated_at",
                    formatters=[(f.DateFormatter, {})],
                ),
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
