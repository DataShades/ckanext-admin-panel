from __future__ import annotations

import logging
from functools import partial

import sqlalchemy as sa
from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.ap_main.utils as ap_utils
import ckanext.tables.shared as t
from ckanext.ap_main import formatters as f
from ckanext.tables.shared import GenericTableView

ap_content = Blueprint("ap_content", __name__, url_prefix="/admin-panel")
ap_content.before_request(ap_utils.ap_before_request)

log = logging.getLogger(__name__)


class ContentTable(t.TableDefinition):
    def __init__(self):
        package_query = model.Session.query(
            model.Package.id.label("id"),
            model.Package.name.label("name"),
            model.Package.title.label("title"),
            model.Package.type.label("type"),
            model.User.id.label("author"),
            model.Package.state.label("state"),
            model.Package.metadata_created.label("metadata_created"),
            model.Package.metadata_modified.label("metadata_modified"),
        ).join(model.User, model.Package.creator_user_id == model.User.id)

        group_query = model.Session.query(
            model.Group.id.label("id"),
            model.Group.name.label("name"),
            model.Group.title.label("title"),
            model.Group.type.label("type"),
            sa.null().label("author"),
            model.Group.state.label("state"),
            model.Group.created.label("metadata_created"),
            model.Group.created.label("metadata_modified"),
        )

        union_query = package_query.union(group_query).subquery()

        super().__init__(
            name="content",
            table_template="admin_panel/tables/table_base.html",
            data_source=t.DatabaseDataSource(
                stmt=sa.select(
                    union_query.c.id,
                    union_query.c.name,
                    union_query.c.title,
                    union_query.c.type,
                    union_query.c.author,
                    union_query.c.state,
                    union_query.c.metadata_created,
                    union_query.c.metadata_modified,
                ).order_by(union_query.c.metadata_modified.desc()),
            ),
            columns=[
                t.ColumnDefinition(field="title"),
                t.ColumnDefinition(field="type", width=100),
                t.ColumnDefinition(
                    field="author", formatters=[(f.UserLinkFormatter, {})], tabulator_formatter="html", width=150
                ),
                t.ColumnDefinition(field="state", resizable=False, width=100),
                t.ColumnDefinition(
                    title="Created at",
                    field="metadata_created",
                    formatters=[(f.DateFormatter, {"date_format": "%Y-%m-%d %H:%M"})],
                    resizable=False,
                    width=160,
                ),
                t.ColumnDefinition(
                    title="Updated at",
                    field="metadata_modified",
                    formatters=[(f.DateFormatter, {"date_format": "%Y-%m-%d %H:%M"})],
                    resizable=False,
                    width=160,
                ),
            ],
            row_actions=[
                t.RowActionDefinition(
                    action="edit",
                    label="Edit",
                    icon="fa fa-pencil",
                    callback=lambda row: t.ActionHandlerResult(
                        success=True,
                        redirect=tk.url_for(
                            "ap_content.entity_proxy",
                            view="edit",
                            entity_type=row["type"],
                            entity_id=row["id"],
                        ),
                    ),
                ),
                t.RowActionDefinition(
                    action="view",
                    label="View",
                    icon="fa fa-eye",
                    callback=lambda row: t.ActionHandlerResult(
                        success=True,
                        redirect=tk.url_for(
                            "ap_content.entity_proxy",
                            view="read",
                            entity_type=row["type"],
                            entity_id=row["id"],
                        ),
                    ),
                ),
            ],
            bulk_actions=[
                t.BulkActionDefinition(
                    action="restore",
                    label="Restore selected entities",
                    callback=partial(self._change_entities_state, is_active=True),
                ),
                t.BulkActionDefinition(
                    action="delete",
                    label="Delete selected entities",
                    callback=partial(self._change_entities_state, is_active=False),
                ),
                t.BulkActionDefinition(
                    action="purge",
                    label="Purge selected entities",
                    callback=self._purge_entities,
                ),
            ],
        )

    def _change_entities_state(self, rows: list[t.Row], is_active: bool = False) -> t.ActionHandlerResult:
        errors = []
        actions = {
            "dataset": "package_patch",
            "organization": "organization_patch",
            "group": "group_patch",
        }

        for row in rows:
            action = actions.get(row["type"])

            if not action:
                errors.append(f"Changing {row['type']} entity state isn't supported")
                continue

            try:
                tk.get_action(action)(
                    {"ignore_auth": True},
                    {
                        "id": row["id"],
                        "state": model.State.ACTIVE if is_active else model.State.DELETED,
                    },
                )
            except tk.ObjectNotFound:
                pass
            except tk.ValidationError as e:
                errors.append(str(e.error_summary))

        if errors:
            return t.ActionHandlerResult(success=False, error="\n".join(errors))

        return t.ActionHandlerResult(success=True)

    def _purge_entities(self, rows: list[t.Row]) -> t.ActionHandlerResult:
        errors = []
        actions = {
            "dataset": "dataset_purge",
            "organization": "organization_purge",
            "group": "group_purge",
        }

        for row in rows:
            action = actions.get(row["type"])

            if not action:
                errors.append(f"Purging {row['type']} entity isn't supported")
                continue

            try:
                tk.get_action(action)({"ignore_auth": True}, {"id": row["id"]})
            except tk.ObjectNotFound:
                pass
            except tk.ValidationError as e:
                errors.append(str(e.error_summary))

        if errors:
            return t.ActionHandlerResult(success=False, error="\n".join(errors))

        return t.ActionHandlerResult(success=True)


class ContentProxyView(MethodView):
    def get(self, view: str, entity_type: str, entity_id: str) -> Response:
        return tk.redirect_to(f"{entity_type}.{view}", id=entity_id)


ap_content.add_url_rule(
    "/content",
    view_func=GenericTableView.as_view("list", table=ContentTable, breadcrumb_label="Content"),
)
ap_content.add_url_rule(
    "/content/<view>/<entity_type>/<entity_id>",
    view_func=ContentProxyView.as_view("entity_proxy"),
)
