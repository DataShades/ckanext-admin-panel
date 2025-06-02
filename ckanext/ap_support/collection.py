from __future__ import annotations

from dominate import tags

import ckan.plugins.toolkit as tk

from ckanext.ap_support.model import Ticket
from ckanext.collection.types import ButtonFilter, InputFilter, SelectFilter
from ckanext.collection.utils import Filters, ModelData

from ckanext.ap_main.collection.base import (
    ApCollection,
    ApColumns,
    ApHtmxTableSerializer,
    BulkAction,
    RowAction,
)


def custom_row_dictizer(serializer: ApHtmxTableSerializer, row: Ticket):
    data = row.dictize({})
    data["bulk-action"] = data["id"]
    data["author"] = data["author"]["name"]

    return data


class SupportCollection(ApCollection):
    SerializerFactory = ApHtmxTableSerializer.with_attributes(
        row_dictizer=custom_row_dictizer
    )

    ColumnsFactory = ApColumns.with_attributes(
        names=[
            "bulk-action",
            "subject",
            "status",
            "author",
            "category",
            "created_at",
            "updated_at",
            "row_actions",
        ],
        sortable={"created_at", "updated_at", "last_run", "state"},
        searchable={"name"},
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
            "subject": "Subject",
            "status": "Status",
            "author": "Author",
            "category": "Category",
            "created_at": "Created N days ago",
            "updated_at": "Updated At",
            "row_actions": "Actions",
        },
        width={
            "created_at": "10%",
            "updated_at": "10%",
            "row_actions": "15%",
        },
        serializers={
            "status": [("ap_support_status", {})],
            "author": [("user_link", {})],
            "created_at": [("day_passed", {})],
            "updated_at": [("date", {})],
        },
    )

    DataFactory = ModelData.with_attributes(
        model=Ticket,
        is_scalar=True,
        use_naive_search=True,
        use_naive_filters=True,
    )

    FiltersFactory = Filters.with_attributes(
        static_actions=[
            BulkAction(
                name="bulk-action",
                type="bulk_action",
                options={
                    "label": "Action",
                    "options": [
                        {"value": "1", "text": "Close selected tickets"},
                        {"value": "2", "text": "Reopen selected tickets"},
                        {"value": "3", "text": "Remove selected tickets"},
                    ],
                },
            ),
            RowAction(
                name="view",
                type="row_action",
                options={
                    "endpoint": "ap_support.ticket_delete",
                    "icon": "fa fa-trash",
                    "params": {
                        "ticket_id": "$id",
                    },
                },
            ),
            RowAction(
                name="view",
                type="row_action",
                options={
                    "endpoint": "ap_support.ticket_read",
                    "label": "View",
                    "params": {
                        "ticket_id": "$id",
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
                        {"value": Ticket.Status.opened, "text": "Opened"},
                        {"value": Ticket.Status.closed, "text": "Closed"},
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
