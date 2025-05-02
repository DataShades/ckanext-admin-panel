import json
import uuid
from abc import abstractmethod
from typing import Any, Callable

import ckan.plugins.toolkit as tk


class ColumnDefinition:
    """Defines how a column should be rendered in Tabulator"""

    def __init__(
        self,
        field: str,
        title: str | None = None,
        formatters: list[tuple[Callable[..., Any], dict[str, Any]]] | None = None,
        tabulator_formatter: str | None = None,
        tabulator_formatter_params: dict[str, Any] | None = None,
        width: int | None = None,
        visible: bool = True,
        sortable: bool = True,
        filterable: bool = True,
        init_htmx: bool = False,
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
            visible (bool): Whether the column is visible
            sortable (bool): Whether the column can be sorted
            filterable (bool): Whether the column can be filtered
        """
        self.field = field
        self.title = title or field.replace("_", " ").title()
        self.formatters = formatters
        self.tabulator_formatter = tabulator_formatter
        self.tabulator_formatter_params = tabulator_formatter_params
        self.width = width
        self.visible = visible
        self.sortable = sortable
        self.filterable = filterable

    def __repr__(self):
        return f"ColumnDefinition(field={self.field}, title={self.title})"

    def to_dict(self):
        """Convert the column definition to a dict for JSON serialization"""
        result = {
            "field": self.field,
            "title": self.title,
            "visible": self.visible,
            "sortable": self.sortable,
            "filterable": self.filterable,
        }

        if self.tabulator_formatter:
            result["formatter"] = self.tabulator_formatter

        if self.tabulator_formatter_params:
            result["formatterParams"] = self.tabulator_formatter_params

        if self.width:
            result["width"] = self.width

        return result


class GlobalActionDefinition:
    """Defines an action that can be performed on multiple rows"""

    def __init__(
        self,
        name: str,
        label: str,
        icon: str | None = None,
        url: str | None = None,
        endpoint: str | None = None,
        method: str = "POST",
        confirm: bool = False,
        confirm_message: str | None = None,
        css_class: str | None = None,
        min_selected: int = 1,
        max_selected: int | None = None,
        visible_callback: Callable | None = None,
    ):
        """
        Initialize a global action definition

        Args:
            name (str): Unique identifier for the action
            label (str): Display label for the action
            icon (str, optional): Icon class (e.g., "fa fa-trash")
            url (str, optional): Static URL for the action
            endpoint (str, optional): Flask endpoint to generate URL
            method (str): HTTP method (POST, PUT, DELETE, etc.)
            confirm (bool): Whether to show a confirmation dialog
            confirm_message (str, optional): Confirmation message
            css_class (str, optional): CSS class for styling
            min_selected (int): Minimum number of rows that must be selected
            max_selected (int, optional): Maximum number of rows that can be selected
            visible_callback (callable, optional): Function that determines if action is visible
        """
        self.name = name
        self.label = label
        self.icon = icon
        self.url = url
        self.endpoint = endpoint
        self.method = method
        self.confirm = confirm
        self.confirm_message = (
            confirm_message
            or f"Are you sure you want to {label.lower()} the selected items?"
        )
        self.css_class = css_class
        self.min_selected = min_selected
        self.max_selected = max_selected
        self.visible_callback = visible_callback

    def __repr__(self):
        return f"GlobalActionDefinition(name={self.name}, label={self.label})"

    def to_dict(self):
        """Convert the global action to a dict for JSON serialization"""
        result = {
            "name": self.name,
            "label": self.label,
            "method": self.method,
            "confirm": self.confirm,
            "minSelected": self.min_selected,
        }

        if self.icon:
            result["icon"] = self.icon

        if self.confirm:
            result["confirmMessage"] = self.confirm_message

        if self.css_class:
            result["cssClass"] = self.css_class

        if self.max_selected:
            result["maxSelected"] = self.max_selected

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
        # method: str = "GET",
        # confirm: bool = False,
        # confirm_message: str | None = None,
        css_class: str | None = None,
        visible_callback: Callable | None = None,
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
        """Convert the action to a dict for JSON serialization"""
        # Check if action should be visible for this row
        if self.visible_callback and row_data and not self.visible_callback(row_data):
            return None

        result = {
            "name": self.name,
            "label": self.label,
            "method": self.method,
            "attrs": self.attrs,
        }

        if self.icon:
            result["icon"] = self.icon

        if self.css_class:
            result["cssClass"] = self.css_class

        return result


class TableDefinition:
    """Defines a table to be rendered with Tabulator"""

    def __init__(
        self,
        name: str,
        title: str | None = None,
        columns: list[ColumnDefinition] | None = None,
        actions: list[ActionDefinition] | None = None,
        global_actions: list[GlobalActionDefinition] | None = None,
        pagination: bool = True,
        page_size: int = 10,
        selectable: bool = False,
        movable_columns: bool = True,
        resizable_columns: bool = True,
    ):
        """
        Initialize a table definition

        Args:
            name (str): Unique identifier for the table
            title (str, optional): Display title for the table
            columns (list, optional): List of ColumnDefinition objects
            actions (list, optional): List of ActionDefinition objects
            global_actions (list, optional): List of GlobalActionDefinition objects
            pagination (bool): Whether to enable pagination
            page_size (int): Number of rows per page
            selectable (bool): Whether rows can be selected
            movable_columns (bool): Whether columns can be reordered
            resizable_columns (bool): Whether columns can be resized
        """
        self.name = name
        self.title = title or name.replace("_", " ").title()
        self.columns = columns or []
        self.actions = actions or []
        self.global_actions = global_actions or []
        self.pagination = pagination
        self.page_size = page_size
        self.selectable = True if self.global_actions else selectable
        self.movable_columns = movable_columns
        self.resizable_columns = resizable_columns

    def get_tabulator_options(self) -> dict[str, Any]:
        columns = [col.to_dict() for col in self.columns]

        options = {
            "columns": columns,
            "layout": "fitDataFill",
            "movableColumns": self.movable_columns,
            "resizableColumns": self.resizable_columns,
        }

        if self.pagination:
            options["pagination"] = "local"
            options["paginationSize"] = self.page_size
            options["paginationSizeSelector"] = [5, 10, 25, 50, 100]

        # Set up selectable options
        if self.selectable or self.global_actions:
            options["selectable"] = True
            options["selectableRangeMode"] = "click"
            options["selectableRollingSelection"] = False
            options["selectablePersistence"] = False

        return options

    def render_table(
        self,
        template: str = "admin_panel/tables/table.html",
        data_url: str | None = None,
        **kwargs: dict[str, Any],
    ) -> str:
        """Render the table template with the necessary data"""

        return tk.render(
            template,
            extra_vars={
                "table_id": f"table_{self.name}_{uuid.uuid4().hex[:8]}",
                "table_name": self.name,
                "table_title": self.title,
                "columns": [col.to_dict() for col in self.columns],
                "tabulator_options": json.dumps(self.get_tabulator_options()),
                "data_url": data_url,
                "global_actions": [action.to_dict() for action in self.global_actions],
                **kwargs,
            },
        )

    @abstractmethod
    def get_raw_data(self) -> list[dict[str, Any]]:
        """Return the list of rows to be rendered in the table

        Returns:
            list[dict[str, Any]]: List of rows to be rendered in the table
        """
        pass

    def get_data(self) -> list[Any]:
        """Get the data for the table with applied formatters"""
        return [self.apply_formatters(dict(row)) for row in self.get_raw_data()]

    def apply_formatters(self, row: dict[str, Any]) -> dict[str, Any]:
        for column in self.columns:
            cell_value = row.get(column.field)

            if not column.formatters:
                continue

            for formatter, formatter_options in column.formatters:
                cell_value = formatter(cell_value, formatter_options, column, row, self)

            row[column.field] = cell_value

        return row
