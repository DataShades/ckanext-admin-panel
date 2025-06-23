from __future__ import annotations

import logging
from functools import partial
from typing import Any, Optional, Union

import sqlalchemy as sa
from flask import Blueprint, Response
from flask.views import MethodView
from typing_extensions import TypeAlias

import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.ap_main.types as types
import ckanext.ap_main.utils as ap_utils
from ckanext.ap_main.table import (
    ActionDefinition,
    ColumnDefinition,
    GlobalActionDefinition,
    TableDefinition,
)
from ckanext.ap_main.views.generics import ApTableView

ContentList: TypeAlias = "list[dict[str, Any]]"

ap_content = Blueprint("ap_content", __name__, url_prefix="/admin-panel")
ap_content.before_request(ap_utils.ap_before_request)

log = logging.getLogger(__name__)


class ContentTable(TableDefinition):
    def __init__(self):
        super().__init__(
            name="content",
            ajax_url=tk.url_for("ap_content.list", data=True),
            columns=[
                ColumnDefinition(field="id", visible=False, filterable=False),
                ColumnDefinition(field="title"),
                ColumnDefinition(field="type"),
                ColumnDefinition(
                    field="author",
                    formatters=[("user_link", {})],
                    tabulator_formatter="html",
                ),
                ColumnDefinition(field="state", resizable=False),
                ColumnDefinition(
                    field="metadata_created",
                    formatters=[("date", {"date_format": "%Y-%m-%d %H:%M"})],
                    resizable=False,
                ),
                ColumnDefinition(
                    field="metadata_modified",
                    formatters=[("date", {"date_format": "%Y-%m-%d %H:%M"})],
                    resizable=False,
                ),
                ColumnDefinition(
                    field="actions",
                    formatters=[("actions", {})],
                    filterable=False,
                    tabulator_formatter="html",
                    sorter=None,
                    resizable=False,
                ),
            ],
            actions=[
                ActionDefinition(
                    name="edit",
                    icon="fa fa-pencil",
                    endpoint="ap_content.entity_proxy",
                    url_params={
                        "view": "edit",
                        "entity_type": "$type",
                        "entity_id": "$id",
                    },
                ),
                ActionDefinition(
                    name="view",
                    icon="fa fa-eye",
                    endpoint="ap_content.entity_proxy",
                    url_params={
                        "view": "read",
                        "entity_type": "$type",
                        "entity_id": "$id",
                    },
                ),
            ],
            global_actions=[
                GlobalActionDefinition(
                    action="restore", label="Restore selected entities"
                ),
                GlobalActionDefinition(
                    action="delete", label="Delete selected entities"
                ),
                GlobalActionDefinition(action="purge", label="Purge selected entities"),
            ],
        )

    def get_raw_data(self) -> list[dict[str, Any]]:
        package_query = model.Session.query(
            model.Package.id.label("id"),
            model.Package.name.label("name"),
            model.Package.title.label("title"),
            model.Package.type.label("type"),
            model.User.name.label("author"),
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

        final_query = model.Session.query(union_query).order_by(
            union_query.c.metadata_modified.desc()
        )

        columns = [
            "id",
            "name",
            "title",
            "type",
            "author",
            "state",
            "metadata_created",
            "metadata_modified",
        ]

        return [dict(zip(columns, row)) for row in final_query.all()]


class ContentListView(ApTableView):
    def get_global_action(self, value: str) -> types.GlobalActionHandler | None:
        return {
            "restore": partial(self._change_entities_state, is_active=True),
            "delete": partial(self._change_entities_state, is_active=False),
            "purge": partial(self._purge_entities),
        }.get(value)

    @staticmethod
    def _change_entities_state(
        row: types.Row, is_active: Optional[bool] = False
    ) -> types.GlobalActionHandlerResult:
        actions = {
            "dataset": "package_patch",
            "organization": "organization_patch",
            "group": "group_patch",
        }
        action = actions.get(row["type"])

        if not action:
            return False, f"Changing {row['type']} entity state isn't supported"

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
            return False, str(e.error_summary)

        return True, None

    @staticmethod
    def _purge_entities(row: types.Row) -> types.GlobalActionHandlerResult:
        actions = {
            "dataset": "dataset_purge",
            "organization": "organization_purge",
            "group": "group_purge",
        }
        action = actions.get(row["type"])

        if not action:
            return False, f"Purging {row['type']} entity isn't supported"

        try:
            tk.get_action(action)({"ignore_auth": True}, {"id": row["id"]})
        except tk.ObjectNotFound:
            pass
        except tk.ValidationError as e:
            return False, str(e.error_summary)

        return True, None


class ContentProxyView(MethodView):
    def get(self, view: str, entity_type: str, entity_id: str) -> Union[str, Response]:
        return tk.redirect_to(f"{entity_type}.{view}", id=entity_id)


ap_content.add_url_rule(
    "/content",
    view_func=ContentListView.as_view(
        "list", table=ContentTable, breadcrumb_label="Content", page_title="Content"
    ),
)
ap_content.add_url_rule(
    "/content/<view>/<entity_type>/<entity_id>",
    view_func=ContentProxyView.as_view("entity_proxy"),
)
