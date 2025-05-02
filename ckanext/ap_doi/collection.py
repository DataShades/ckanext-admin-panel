from __future__ import annotations

from dominate import tags

import ckan.plugins.toolkit as tk

from ckanext.ap_doi.utils import DOIProblemPackageData
from ckanext.collection.types import ButtonFilter, InputFilter, SelectFilter
from ckanext.collection.utils import ApiData, Filters

import ckanext.ap_main.collection.base as collection_base


def row_dictizer(
    serializer: collection_base.ApHtmxTableSerializer, row: DOIProblemPackageData
):
    row["bulk-action"] = row["id"]  # type: ignore

    return row


class ApDOICollection(collection_base.ApCollection):
    SerializerFactory = collection_base.ApHtmxTableSerializer.with_attributes(
        row_dictizer=row_dictizer,
    )

    ColumnsFactory = collection_base.ApColumns.with_attributes(
        names=[
            "bulk-action",
            "title",
            "doi_status",
            "identifier",
            "timestamp",
            "published",
            "row_actions",
        ],
        sortable={},
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
            "doi_status": "Status",
            "identifier": "DOI",
            "timestamp": "Timestamp",
            "published": "Publish Date",
            "row_actions": "Actions",
        },
        width={
            "bulk-action": "3%",
            "title": "15%",
            "doi_status": "10%",
            "row_actions": "20%",
        },
        serializers={
            "timestamp": [("date", {})],
            "published": [("date", {})],
        },
    )

    DataFactory = ApiData.with_attributes(
        action="ap_doi_get_packages_doi",
    )

    FiltersFactory = Filters.with_attributes(
        static_actions=[
            collection_base.BulkAction(
                name="bulk-action",
                type="bulk_action",
                options={
                    "label": "Action",
                    "options": [
                        {"value": "1", "text": "Update DOI"},
                    ],
                },
            ),
            collection_base.RowAction(
                name="view",
                type="row_action",
                options={
                    "endpoint": "doi_dashboard.create_or_update_doi",
                    "label": "Update DOI",
                    "params": {
                        "package_id": "$id",
                    },
                },
            ),
            collection_base.RowAction(
                name="view",
                type="row_action",
                options={
                    "endpoint": "ap_content.entity_proxy",
                    "label": "View",
                    "params": {
                        "entity_id": "$name",
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
                name="doi_status",
                type="select",
                options={
                    "label": "Status",
                    "options": [
                        {"value": "", "text": "Any"},
                        {"value": "Published", "text": "Published"},
                        {"value": "Missing", "text": "Missing"},
                        {"value": "Outdated", "text": "Outdated"},
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
