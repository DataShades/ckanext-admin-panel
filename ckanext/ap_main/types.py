from __future__ import annotations

from typing import Any, Callable, Optional, TypedDict

from typing_extensions import TypeAlias

from ckanext.ap_main.table import ColumnDefinition, TableDefinition

ItemList: TypeAlias = "list[dict[str, Any]]"
Item: TypeAlias = "dict[str, Any]"
ItemValue: TypeAlias = Any

Value: TypeAlias = Any
Options: TypeAlias = "dict[str, Any]"
Row: TypeAlias = dict[str, Any]
GlobalActionHandlerResult: TypeAlias = tuple[bool, str | None]
GlobalActionHandler: TypeAlias = Callable[[Row], GlobalActionHandlerResult]
FormatterResult: TypeAlias = str

Formatter: TypeAlias = Callable[
    [Value, Options, ColumnDefinition, Row, TableDefinition],
    FormatterResult,
]


class SectionConfig(TypedDict):
    name: str
    configs: list["ConfigurationItem"]


class ConfigurationItem(TypedDict, total=False):
    name: str
    blueprint: str
    info: Optional[str]


class ToolbarButton(TypedDict, total=False):
    label: str
    url: Optional[str]
    icon: Optional[str]
    aria_label: Optional[str]
    attributes: Optional[dict[str, Any]]
    subitems: list["ToolbarButton"]
