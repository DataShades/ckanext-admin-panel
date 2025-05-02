from __future__ import annotations

import sqlalchemy as sa
from dominate import tags

import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.collection.shared import configurable_attribute
from ckanext.collection.types import ButtonFilter, InputFilter, SelectFilter
from ckanext.collection.utils import Filters, ModelData

from .base import ApCollection, BulkAction, RowAction


class UserCollection(ApCollection):
    ColumnsFactory = ApCollection.ColumnsFactory.with_attributes(
        names=[
            "bulk-action",
            "name",
            "fullname",
            "email",
            "state",
            "sysadmin",
            "row_actions",
        ],
        sortable={
            "name",
            "fullname",
            "email",
            "state",
            "sysadmin",
        },
        width={"bulk-action": "3%"},
        searchable={"name", "fullname"},
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
            "name": "Username",
            "fullname": "Full Name",
            "email": "Email",
            "state": "State",
            "sysadmin": "Sysadmin",
            "row_actions": "Actions",
        },
        serializers={
            "name": [("user_link", {})],
            "fullname": [("none_as_empty", {})],
            "email": [("none_as_empty", {})],
            "sysadmin": [("bool", {})],
        },
    )

    DataFactory = ModelData.with_attributes(
        use_naive_filters=True,
        use_naive_search=True,
        model=model.User,
        static_columns=[
            *sa.inspect(model.User).columns,
            model.User.id.label("bulk-action"),
        ],
        static_filters=configurable_attribute(
            default_factory=lambda self: [model.User.name != tk.config["ckan.site_id"]]
        ),
    )

    FiltersFactory = Filters.with_attributes(
        static_actions=[
            BulkAction(
                name="bulk-action",
                type="bulk_action",
                options={
                    "label": "Action",
                    "options": [
                        {
                            "value": "1",
                            "text": "Add the sysadmin role to the selected user(s)",
                        },
                        {
                            "value": "2",
                            "text": "Remove the sysadmin role from the selected user(s)",
                        },
                        {"value": "3", "text": "Block the selected user(s)"},
                        {"value": "4", "text": "Unblock the selected user(s)"},
                    ],
                },
            ),
            RowAction(
                name="edit",
                type="row_action",
                options={
                    "endpoint": "user.edit",
                    "label": "Edit",
                    "params": {"id": "$id"},
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
                name="sysadmin",
                type="select",
                options={
                    "label": "Role",
                    "options": [
                        {"value": "", "text": "Any"},
                        {"value": "t", "text": "Sysadmin"},
                        {"value": "f", "text": "User"},
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
                        "onclick": "$(this).closest('form').find('input,select').val('').prevObject[0].requestSubmit()"
                    },
                },
            ),
        ],
    )
