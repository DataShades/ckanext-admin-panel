from __future__ import annotations

import logging
from typing import Any, Iterable, Sequence

import sqlalchemy as sa

from ckan import model

from ckanext.ap_log.model import ApLogs
from ckanext.collection.types import (ButtonFilter, Filter, InputFilter,
                                      SelectOption)
from ckanext.collection.utils import Filters, ModelData

from ckanext.ap_main.collection.base import (ApCollection, GlobalAction,
                                             MultiSelectFilter)


class DbLogCollection(ApCollection):
    ColumnsFactory = ApCollection.ColumnsFactory.with_attributes(
        names=[
            "name",
            "path",
            "level",
            "timestamp",
            "message",
        ],
        sortable={
            "name",
            "path",
            "level",
            "timestamp",
        },
        searchable={"message"},
        labels={
            "name": "Name",
            "path": "Path",
            "level": "Level",
            "timestamp": "Timestamp",
            "message": "Message",
        },
        serializers={
            "level": [("log_level", {})],
            "timestamp": [("date", {})],
        },
    )

    DataFactory = ModelData.with_attributes(
        use_naive_filters=True,
        use_naive_search=True,
        is_scalar=True,
        model=ApLogs,
    )

    class FiltersFactory(Filters["DbLogCollection"]):
        def make_actions(self) -> Sequence[Filter[Any]]:
            return [
                GlobalAction(
                    name="clear_logs",
                    type="global_action",
                    options={
                        "label": "Clear logs",
                        "attrs": {
                            "type": "submit",
                            "class": "btn btn-danger",
                            "data-module": "ap-confirm-action",
                            "data-module-content": (
                                "Are you sure you want to clear all logs?"
                            ),
                            "data-module-with-data": "true",
                        },
                    },
                )
            ]

        def make_filters(self) -> Sequence[Filter[Any]]:
            log_type_options: Iterable[SelectOption] = [
                {"value": v, "text": v}
                for v in model.Session.scalars(sa.select(sa.distinct(ApLogs.name)))
            ]

            return [
                InputFilter(
                    name="q",
                    type="input",
                    options={
                        "label": "Search",
                        "placeholder": "Search",
                    },
                ),
                MultiSelectFilter(
                    name="level",
                    type="multiselect",
                    options={
                        "label": "Level",
                        "options": [
                            {"value": str(logging.NOTSET), "text": "NOTSET"},
                            {"value": str(logging.DEBUG), "text": "DEBUG"},
                            {"value": str(logging.INFO), "text": "INFO"},
                            {"value": str(logging.WARNING), "text": "WARNING"},
                            {"value": str(logging.ERROR), "text": "ERROR"},
                            {"value": str(logging.CRITICAL), "text": "CRITICAL"},
                        ],
                    },
                ),
                MultiSelectFilter(
                    name="name",
                    type="multiselect",
                    options={
                        "label": "Type",
                        "options": log_type_options,
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
            ]
