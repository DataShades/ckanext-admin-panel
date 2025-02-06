from __future__ import annotations

import sqlalchemy as sa
from dominate import tags

import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.collection.types import InputFilter, ButtonFilter, SelectFilter
from ckanext.collection.utils import Filters, UnionSaData

from .base import ApCollection, BulkAction, RowAction


class ContentCollection(ApCollection):
    ColumnsFactory = ApCollection.ColumnsFactory.with_attributes(
        names=[
            "bulk-action",
            "title",
            "notes",
            "type",
            "creator_user_id",
            "state",
            "metadata_created",
            "metadata_modified",
            "row_actions",
        ],
        sortable={
            "title",
            "type",
            "state",
            "metadata_created",
            "metadata_modified",
        },
        width={"bulk-action": "3%", "title": "15%", "notes": "20%", "row_actions": "15%"},
        searchable={"title", "notes"},
        labels={
            "bulk-action": tk.literal(
                tags.input_(
                    type="checkbox",
                    name="bulk_check",
                    id="bulk_check",
                    data_module="ap-bulk-check",
                    data_module_selector='input[name="entity_id"]',
                )
            ),
            "title": "Title",
            "notes": "Notes",
            "type": "Type",
            "creator_user_id": "Author",
            "state": "State",
            "metadata_created": "Created at",
            "metadata_modified": "Modified at",
            "row_actions": "Actions",
        },
        serializers={
            "notes": [("trim_string", {"max_length": 100})],
            "creator_user_id": [("user_link", {})],
            "metadata_created": [("date", {})],
            "metadata_modified": [("date", {})],
        },
    )

    DataFactory = UnionSaData.with_attributes(
        use_naive_filters=True,
        use_naive_search=True,
        statements=[
            model.Session.query(
                model.Package.id.label("id"),
                sa.func.concat(model.Package.id, "|", model.Package.type).label(
                    "bulk-action"
                ),
                model.Package.name.label("name"),
                model.Package.title.label("title"),
                model.Package.notes.label("notes"),
                model.Package.type.label("type"),
                model.Package.creator_user_id.label("creator_user_id"),
                model.Package.state.label("state"),
                model.Package.metadata_created.label("metadata_created"),
                model.Package.metadata_modified.label("metadata_modified"),
            ),
            model.Session.query(
                model.Group.id.label("id"),
                sa.func.concat(model.Group.id, "|", model.Group.type).label(
                    "bulk-action"
                ),
                model.Group.name.label("name"),
                model.Group.title.label("title"),
                model.Group.description.label("notes"),
                model.Group.type.label("type"),
                sa.null().label("creator_user_id"),
                model.Group.state.label("state"),
                model.Group.created.label("metadata_created"),
                model.Group.created.label("metadata_modified"),
            ),
        ],
    )

    FiltersFactory = Filters.with_attributes(
        static_actions=[
            BulkAction(
                name="bulk-action",
                type="bulk_action",
                options={
                    "label": "Action",
                    "options": [
                        {"value": "1", "text": "Restore selected entities(s)"},
                        {"value": "2", "text": "Delete selected entities(s)"},
                        {"value": "3", "text": "Purge selected entities(s)"},
                    ],
                },
            ),
            RowAction(
                name="edit",
                type="row_action",
                options={
                    "endpoint": "ap_content.entity_proxy",
                    "label": "Edit",
                    "params": {
                        "entity_id": "$id",
                        "entity_type": "$type",
                        "view": "edit",
                    },
                },
            ),
            RowAction(
                name="view",
                type="row_action",
                options={
                    "endpoint": "ap_content.entity_proxy",
                    "label": "View",
                    "params": {
                        "entity_id": "$id",
                        "entity_type": "$type",
                        "view": "read",
                    },
                },
            ),
        ],
        static_filters=[
            InputFilter(
                name="q",
                type="input",
                options={
                    "label": "Search",
                    "placeholder": "Search",
                },
            ),
            SelectFilter(
                name="state",
                type="select",
                options={
                    "label": "State",
                    "options": [
                        {"value": "", "text": "Any"},
                        {"value": model.State.DELETED, "text": "Deleted"},
                        {"value": model.State.ACTIVE, "text": "Active"},
                    ],
                },
            ),
            SelectFilter(
                name="type",
                type="select",
                options={
                    "label": "Type",
                    "options": [
                        {"value": "", "text": "Any"},
                        {"value": "dataset", "text": "Dataset"},
                        {"value": "group", "text": "Group"},
                        {"value": "organization", "text": "Organization"},
                    ],
                },
            ),
            ButtonFilter(
                name="type",
                type="button",
                options={
                    "label": "Clear",
                    "type": "button",
                    "attrs": {
                        "onclick": "$(this).closest('form').find('input,select').val('').prevObject[0].requestSubmit()",
                        "class": "btn btn-outline-primary",
                    },
                },
            ),
        ],
    )
