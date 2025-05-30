from __future__ import annotations

from typing import Any, Optional, TypedDict

from typing_extensions import TypeAlias

from ckanext.collection.types import ValueSerializer

ItemList: TypeAlias = "list[dict[str, Any]]"
Item: TypeAlias = "dict[str, Any]"
ItemValue: TypeAlias = Any

ColRenderer: TypeAlias = ValueSerializer


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
