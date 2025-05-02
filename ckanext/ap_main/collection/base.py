from __future__ import annotations

from typing import Any, Literal, Sequence

from typing_extensions import NotRequired, TypedDict

from ckanext.collection.shared import configurable_attribute
from ckanext.collection.types import (Filter, SelectFilterOptions,
                                      TDataCollection)
from ckanext.collection.utils import Collection, Columns, HtmxTableSerializer

from ckanext.ap_main.utils import get_all_renderers


class ApColumns(Columns[TDataCollection]):
    width = configurable_attribute(default_factory=lambda self: {})


class ApHtmxTableSerializer(HtmxTableSerializer[TDataCollection]):
    """Main table serializer.

    For now it just customizes standard HtmxTableSerializer. No new attributes,
    no new functions.

    Because `ensure_dictized` flag enabled, all records inside
    `record_template` are available as dictionaries. This is done intentionaly,
    for compatibility with CKAN v2.11. Here's an example of change in logic:

    >>> record = model.Session.query(User.id, User.name).first()
    >>> # v2.10
    >>> id, name = record.id, record.name
    >>>
    >>> # v2.11
    >>> id, name = record[0], record[1]

    When you query separate columns of the model, you are no longer allowed to
    access columns by their original name. Now you have to use index of the
    column instead. Such restriction will certainly decrease readability of
    templates, so we are using `ensure_dictized` to convert each record into a
    dictionary with all original column names available.

    """

    base_class: str = configurable_attribute("ap-collection")

    ensure_dictized = configurable_attribute(True)
    push_url = True

    main_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/main.html",
    )

    table_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/table.html",
    )

    record_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/record.html",
    )
    form_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/form.html",
    )
    action_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/action.html",
    )
    filter_template: str = configurable_attribute(
        "collection/serialize/ap_htmx_table/filter.html",
    )

    value_serializers = configurable_attribute(
        default_factory=lambda self: get_all_renderers()
    )


class ApCollection(Collection):
    SerializerFactory = ApHtmxTableSerializer
    ColumnsFactory = ApColumns


class BulkActionOptions(TypedDict):
    """Options of the bulk_action filter."""

    label: str
    options: Sequence[dict[str, Any]]


class RowActionOptions(TypedDict):
    """Options of the row_action filter."""

    endpoint: str
    label: str
    params: dict[str, Any]
    icon: NotRequired[str]


class GlobalActionOptions(TypedDict):
    """Options of the global_action filter."""

    label: str
    attrs: dict[str, Any]


class RowAction(Filter[RowActionOptions]):
    type: Literal["row_action"]


class BulkAction(Filter[BulkActionOptions]):
    type: Literal["bulk_action"]


class GlobalAction(Filter[GlobalActionOptions]):
    type: Literal["global_action"]


class MultiSelectFilter(Filter[SelectFilterOptions]):
    type: Literal["multiselect"]
