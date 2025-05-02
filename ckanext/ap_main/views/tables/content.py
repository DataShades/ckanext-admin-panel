from __future__ import annotations

import logging
from typing import Any, Union

import sqlalchemy as sa
from flask import Blueprint, Response, jsonify
from flask.views import MethodView
from typing_extensions import TypeAlias

import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.ap_main.utils as ap_utils
import ckanext.ap_main.views.tables.formatters as formatters
from ckanext.ap_main.views.tables.table import (ActionDefinition,
                                                ColumnDefinition,
                                                TableDefinition)

ContentList: TypeAlias = "list[dict[str, Any]]"

ap_content = Blueprint("ap_content", __name__, url_prefix="/admin-panel")
ap_content.before_request(ap_utils.ap_before_request)

log = logging.getLogger(__name__)


class ContentTable(TableDefinition):
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

        return [dict(row) for row in package_query.union(group_query).all()]


class ContentListView(MethodView):
    def get(self) -> Union[str, Response]:
        table = self.get_table()

        if tk.request.args.get("data"):
            return jsonify({"success": True, "data": table.get_data()})

        return table.render_table(data_url=tk.url_for("ap_content.list", data=True))

    def get_table(self) -> TableDefinition:
        table = ContentTable(
            name="content",
            title="Content",
            page_size=10,
            columns=[
                ColumnDefinition(field="id", visible=False, filterable=False),
                ColumnDefinition(field="title"),
                ColumnDefinition(field="type"),
                ColumnDefinition(
                    field="author",
                    formatters=[(formatters.user_link, {})],
                    tabulator_formatter="html",
                ),
                ColumnDefinition(field="state"),
                ColumnDefinition(
                    field="metadata_created",
                    formatters=[
                        (formatters.date, {"date_format": "%Y-%m-%d %H:%M:%S"})
                    ],
                ),
                ColumnDefinition(
                    field="metadata_modified",
                    formatters=[
                        (formatters.date, {"date_format": "%Y-%m-%d %H:%M:%S"})
                    ],
                ),
                ColumnDefinition(
                    field="actions",
                    formatters=[(formatters.actions, {})],
                    filterable=False,
                    tabulator_formatter="html",
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
        )

        return table

    # def post(self) -> Response:
    #     bulk_action = tk.request.form.get("bulk-action")
    #     content_ids_to_types = tk.request.form.getlist("entity_id")
    #     action_func = self._get_bulk_action(bulk_action) if bulk_action else None

    #     if not action_func:
    #         tk.h.flash_error(tk._("The bulk action is not implemented"))
    #         return tk.redirect_to("ap_content.list")

    #     for entity_type, entity_ids in self._group_entity_ids_by_types(
    #         content_ids_to_types
    #     ).items():
    #         try:
    #             if action_func(entity_ids, entity_type):
    #                 tk.h.flash_success(tk._("Done."))
    #         except tk.ValidationError as e:
    #             tk.h.flash_error(str(e))

    #     return tk.redirect_to("ap_content.list")

    # def _group_entity_ids_by_types(
    #     self, ids_to_types: list[str]
    # ) -> dict[str, list[str]]:
    #     result: dict[str, list[str]] = {}

    #     for row in ids_to_types:
    #         try:
    #             entity_id, entity_type = row.split("|")
    #         except ValueError:
    #             continue

    #         result.setdefault(entity_type, [])
    #         result[entity_type].append(entity_id)

    #     return result

    # def _get_bulk_action(self, value: str) -> Callable[[list[str], str], bool] | None:
    #     return {
    #         "1": partial(self._change_entities_state, is_active=True),
    #         "2": partial(self._change_entities_state, is_active=False),
    #         "3": partial(self._purge_entities),
    #     }.get(value)

    # @staticmethod
    # def _change_entities_state(
    #     entity_ids: list[str], entity_type: str, is_active: Optional[bool] = False
    # ) -> bool:
    #     state = model.State.ACTIVE if is_active else model.State.DELETED
    #     actions = {
    #         "dataset": "package_patch",
    #         "organization": "organization_patch",
    #         "group": "group_patch",
    #     }
    #     action = actions.get(entity_type)

    #     if not action:
    #         tk.h.flash_error(f"Changing {entity_type} entity state isn't supported")
    #         return False

    #     for entity_id in entity_ids:
    #         try:
    #             logic.get_action(action)(
    #                 {"ignore_auth": True},
    #                 {"id": entity_id, "state": state},
    #             )
    #         except tk.ObjectNotFound:
    #             pass

    #     return True

    # @staticmethod
    # def _purge_entities(entity_ids: list[str], entity_type: str) -> bool:
    #     actions = {
    #         "dataset": "dataset_purge",
    #         "organization": "organization_purge",
    #         "group": "group_purge",
    #     }
    #     action = actions.get(entity_type)

    #     if not action:
    #         tk.h.flash_error(f"Purging {entity_type} entity isn't supported")
    #         return False

    #     for entity_id in entity_ids:
    #         try:
    #             logic.get_action(action)(
    #                 {"ignore_auth": True},
    #                 {"id": entity_id},
    #             )
    #         except tk.ObjectNotFound:
    #             pass

    #     return True


class ContentProxyView(MethodView):
    def get(self, view: str, entity_type: str, entity_id: str) -> Union[str, Response]:
        return tk.redirect_to(f"{entity_type}.{view}", id=entity_id)


ap_content.add_url_rule("/content", view_func=ContentListView.as_view("list"))
ap_content.add_url_rule(
    "/content/<view>/<entity_type>/<entity_id>",
    view_func=ContentProxyView.as_view("entity_proxy"),
)
