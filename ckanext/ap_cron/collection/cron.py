from __future__ import annotations

import sqlalchemy as sa
from dominate import tags

import ckan.plugins.toolkit as tk

from ckanext.ap_cron.model import CronJob
from ckanext.collection.types import ButtonFilter, InputFilter, SelectFilter
from ckanext.collection.utils import Filters, StatementSaData

from ckanext.ap_main.collection.base import (ApCollection, ApColumns,
                                             ApHtmxTableSerializer, BulkAction)


class CronCollection(ApCollection):
    SerializerFactory = ApHtmxTableSerializer.with_attributes(
        record_template="ap_cron/cron_record.html"
    )

    ColumnsFactory = ApColumns.with_attributes(
        names=[
            "bulk-action",
            "name",
            "actions",
            "data",
            "schedule",
            "updated_at",
            "last_run",
            "state",
            "row_actions",
        ],
        sortable={"name", "updated_at", "last_run", "state"},
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
            "name": "Name",
            "actions": "Actions",
            "data": "Data",
            "schedule": "schedule",
            "updated_at": "Updated At",
            "last_run": "Last run",
            "state": "State",
            "row_actions": "Actions",
        },
        width={
            "bulk-action": "3%",
            "data": "30%",
            "row_actions": "15%",
        },
        serializers={
            "data": [("json_display", {})],
            "schedule": [("schedule", {})],
            "updated_at": [("date", {})],
            "last_run": [("last_run", {})],
        },
    )

    DataFactory = StatementSaData.with_attributes(
        model=CronJob,
        use_naive_filters=True,
        use_naive_search=True,
        statement=sa.select(
            CronJob.id.label("bulk-action"),
            CronJob.id.label("id"),
            CronJob.name.label("name"),
            CronJob.actions.label("actions"),
            CronJob.data.label("data"),
            CronJob.schedule.label("schedule"),
            CronJob.updated_at.label("updated_at"),
            CronJob.last_run.label("last_run"),
            CronJob.state.label("state"),
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
                        {"value": "1", "text": "Disable selected job"},
                        {"value": "2", "text": "Enable selected job"},
                        {"value": "3", "text": "Delete selected job"},
                    ],
                },
            )
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
                        {"value": CronJob.State.active, "text": "Active"},
                        {"value": CronJob.State.disabled, "text": "Disabled"},
                        {"value": CronJob.State.pending, "text": "Pending"},
                        {"value": CronJob.State.running, "text": "Running"},
                        {"value": CronJob.State.failed, "text": "Failed"},
                        {"value": CronJob.State.finished, "text": "Finished"},
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
