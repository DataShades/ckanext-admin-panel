from __future__ import annotations

from typing import Any

from ckan.plugins.interfaces import Interface

import ckanext.ap_main.types as ap_types


class IAdminPanel(Interface):
    """Extends the functionallity of the Admin Panel."""

    def register_toolbar_button(
        self, toolbar_buttons_list: list[ap_types.ToolbarButton]
    ) -> list[ap_types.ToolbarButton]:
        """Register toolbar buttons.

        Extension will receive the list of toolbar button objects. It can
        modify the list and return it back.

        Example:
            ```python
            import ckanext.ap_main.types as ap_types

            def register_toolbar_button(toolbar_buttons_list):
                toolbar_buttons_list.append(
                    ap_types.ToolbarButton(
                        label='My Button',
                        url=tk.h.url_for('my_controller.my_action'),
                        icon='fa-star',
                        attributes={'class': 'text'},
                    )
                )
                return toolbar_buttons_list
            ```

        Returns:
            A list of toolbar button objects
        """
        return toolbar_buttons_list

    def get_formatters(self) -> dict[str, ap_types.Formatter]:
        """Allows an extension to register its own tabulator formatters.

        Example:
            ```python
            def get_formatters():
                return {'col_counter': col_counter}
            ```

        Returns:
            A mapping of formatter names to tabulator formatter functions
        """
        return {}

    def before_config_update(self, schema_id: str, data: dict[str, Any]) -> None:
        """Called before generic view configuration update.

        Could be used to modify configuration data before it is saved.

        Args:
            schema_id : an arbitrary schema ID
            data : a dictionary with configuration data

        Example:
            ```python
            def before_config_update(schema_id, data):
                if schema_id == 'my_schema':
                    data['my_field'] = 'my_value'
            ```
        """
        pass

    def after_config_update(
        self, schema_id: str, data_before_update: dict[str, Any], data: dict[str, Any]
    ) -> None:
        """Called after generic view configuration update.

        Could be used to perform additional actions after configuration update.

        Args:
            schema_id : an arbitrary schema ID
            data_before_update : a dictionary with configuration data before update
            data : a dictionary with configuration data after update

        Example:
            ```python
            def after_config_update(schema_id, data_before_update, data):
                if schema_id == 'my_schema':
                    do_something()
            ```
        """
        pass
