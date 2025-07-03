from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import Any, Callable

import ckan.plugins.toolkit as tk


class TableDefinition:
    """Defines a table to be rendered with Tabulator"""

    def __init__(
        self,
        name: str,
        ajax_url: str,
        columns: list[ColumnDefinition] | None = None,
        actions: list[ActionDefinition] | None = None,
        global_actions: list[GlobalActionDefinition] | None = None,
        placeholder: str | None = None,
        pagination: bool = True,
        page_size: int = 10,
        selectable: bool = False,
        table_action_snippet: str | None = None,
        table_template: str = "admin_panel/tables/table_base.html",
    ):
        """
        Initialize a table definition

        Args:
            name (str): Unique identifier for the table
            ajax_url (str): URL to fetch data from
            columns (list, optional): List of ColumnDefinition objects
            actions (list, optional): List of ActionDefinition objects
            global_actions (list, optional): List of GlobalActionDefinition objects
            placeholder (str, optional): Placeholder text for the table
            pagination (bool): Whether to enable pagination
            page_size (int): Number of rows per page
            selectable (bool): Whether rows can be selected
            table_action_snippet (str, optional): Snippet to render table actions
            template (str, optional): Template to render the table
        """
        self.id = f"table_{name}_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.ajax_url = ajax_url
        self.columns = columns or []
        self.actions = actions or []
        self.global_actions = global_actions or []
        self.placeholder = placeholder or "No data found"
        self.pagination = pagination
        self.page_size = page_size
        self.selectable = True if self.global_actions else selectable
        self.table_action_snippet = table_action_snippet
        self.table_template = table_template

    def get_tabulator_config(self) -> dict[str, Any]:
        columns = [col.to_dict() for col in self.columns]

        options = {
            "columns": columns,
            "layout": "fitDataFill",
            "placeholder": self.placeholder,
            "ajaxURL": self.ajax_url,
        }

        if self.pagination:
            options["pagination"] = "local"
            options["paginationSize"] = self.page_size
            options["paginationSizeSelector"] = [5, 10, 25, 50, 100]

        if self.selectable or self.global_actions:
            options["selectableRows"] = True
            options["selectableRangeMode"] = "click"
            options["selectableRollingSelection"] = False
            options["selectablePersistence"] = False

        return options

    def render_table(self, **kwargs: Any) -> str:
        """Render the table template with the necessary data"""

        return tk.render(self.table_template, extra_vars={"table": self, **kwargs})

    @abstractmethod
    def get_raw_data(self) -> list[dict[str, Any]]:
        """Return the list of rows to be rendered in the table

        Returns:
            list[dict[str, Any]]: List of rows to be rendered in the table
        """

    def get_data(self) -> list[Any]:
        """Get the data for the table with applied formatters"""
        self._formatters = tk.h.ap_get_all_formatters()

        return [self.apply_formatters(dict(row)) for row in self.get_raw_data()]

    def apply_formatters(self, row: dict[str, Any]) -> dict[str, Any]:
        """Apply formatters to each cell in a row"""
        for column in self.columns:
            cell_value = row.get(column.field)

            if not column.formatters:
                continue

            for formatter, formatter_options in column.formatters:
                formatter_function = self._formatters[formatter]

                cell_value = formatter_function(
                    cell_value, formatter_options, column, row, self
                )

            row[column.field] = cell_value

        return row


class ColumnDefinition:
    """Defines how a column should be rendered in Tabulator"""

    def __init__(
        self,
        field: str,
        title: str | None = None,
        formatters: list[tuple[str, dict[str, Any]]] | None = None,
        tabulator_formatter: str | None = None,
        tabulator_formatter_params: dict[str, Any] | None = None,
        width: int | None = None,
        min_width: int | None = None,
        visible: bool = True,
        sorter: str | None = "string",
        filterable: bool = True,
        resizable: bool = True,
    ):
        """
        Initialize a column definition

        Args:
            field (str): The field name in the data dict
            title (str, optional): The display title for the column
            formatters (list, optional): List of formatters to apply to the column
            tabulator_formatter (str, optional): Tabulator formatter to apply to the column
            tabulator_formatter_params (dict, optional): Parameters for the tabulator formatter
            width (int, optional): Width of the column
            min_width (int, optional): Minimum width of the column
            visible (bool): Whether the column is visible
            sorter (str, optional): Default sorter for the column
            filterable (bool): Whether the column can be filtered
            resizable (bool): Whether the column is resizable
        """
        self.field = field
        self.title = title or field.replace("_", " ").title()
        self.formatters = formatters
        self.tabulator_formatter = tabulator_formatter
        self.tabulator_formatter_params = tabulator_formatter_params
        self.width = width
        self.min_width = min_width
        self.visible = visible
        self.sorter = sorter
        self.filterable = filterable
        self.resizable = resizable

    def __repr__(self):
        return f"ColumnDefinition(field={self.field}, title={self.title})"

    def to_dict(self) -> dict[str, Any]:
        """Convert the column definition to a dict for JSON serialization"""
        result = {
            "field": self.field,
            "title": self.title,
            "visible": self.visible,
            "resizable": self.resizable,
        }

        if self.sorter:
            result["sorter"] = self.sorter
        else:
            result["headerSort"] = False

        if self.tabulator_formatter:
            result["formatter"] = self.tabulator_formatter

        if self.tabulator_formatter_params:
            result["formatterParams"] = self.tabulator_formatter_params

        if self.width:
            result["width"] = self.width

        if self.min_width:
            result["minWidth"] = self.min_width

        return result


class ActionDefinition:
    """Defines an action that can be performed on a row"""

    def __init__(
        self,
        name: str,
        label: str | None = None,
        icon: str | None = None,
        url: str | None = None,
        endpoint: str | None = None,
        url_params: dict[str, Any] | None = None,
        css_class: str | None = None,
        visible_callback: Callable[..., bool] | None = None,
        attrs: dict[str, Any] | None = None,
    ):
        """
        Initialize an action definition

        Args:
            name (str): Unique identifier for the action
            label (str, optional): Display label for the action
            icon (str, optional): Icon class (e.g., "fa fa-edit")
            url (str, optional): Static URL for the action
            endpoint (str, optional): Flask endpoint to generate URL
            url_params (dict, optional): Parameters for the URL
            css_class (str, optional): CSS class for styling
            visible_callback (callable, optional): Function that determines if action is visible
            attrs (dict, optional): Additional attributes for the action
        """
        self.name = name
        self.label = label
        self.icon = icon
        self.url = url
        self.endpoint = endpoint
        self.url_params = url_params
        self.css_class = css_class
        self.visible_callback = visible_callback
        self.attrs = attrs or {}

    def __repr__(self):
        return f"ActionDefinition(name={self.name})"

    def to_dict(self, row_data=None):
        # Check if action should be visible for this row
        if self.visible_callback and row_data and not self.visible_callback(row_data):
            return None

        result = {
            "name": self.name,
            "label": self.label,
            "attrs": self.attrs,
        }

        if self.icon:
            result["icon"] = self.icon

        if self.css_class:
            result["cssClass"] = self.css_class

        return result


class GlobalActionDefinition:
    """Defines an action that can be performed on multiple rows"""

    def __init__(
        self,
        action: str,
        label: str,
    ):
        """
        Initialize a global action definition

        Args:
            action (str): Unique identifier for the action
            label (str): Display label for the action
        """
        self.action = action
        self.label = label

    def __repr__(self):
        return f"GlobalActionDefinition(action={self.action}, label={self.label})"

    def to_dict(self):
        return {
            "action": self.action,
            "label": self.label,
        }
