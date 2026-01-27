from __future__ import annotations

from typing import Any, Callable, TypeAlias, TypedDict

ItemList: TypeAlias = "list[dict[str, Any]]"
Item: TypeAlias = "dict[str, Any]"
ItemValue: TypeAlias = Any

Value: TypeAlias = Any
Options: TypeAlias = "dict[str, Any]"
Row: TypeAlias = dict[str, Any]
GlobalActionHandlerResult: TypeAlias = tuple[bool, str | None]
GlobalActionHandler: TypeAlias = Callable[[Row], GlobalActionHandlerResult]
FormatterResult: TypeAlias = str


class SectionConfig(TypedDict):
    name: str
    configs: list[ConfigurationItem]


class ConfigurationItem(TypedDict, total=False):
    name: str
    blueprint: str
    info: str | None


class ToolbarButton(TypedDict, total=False):
    label: str
    url: str | None
    icon: str | None
    aria_label: str | None
    attributes: dict[str, Any] | None
    subitems: list[ToolbarButton]
