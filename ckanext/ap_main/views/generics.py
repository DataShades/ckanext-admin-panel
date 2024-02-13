from __future__ import annotations

from typing import Any

from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.logic import parse_params


class ApConfigurationPageView(MethodView):
    def __init__(
        self,
        schema_id: str,
        render_template: str = "admin_panel/config/autogenerated_config.html",
        breadcrum_label: str = "Configuration",
        page_title: str = "Configuration page",
        success_update_message: str = "Config options have been updated",
        fields: list[dict[str, Any]] = None,
    ):
        """A generic view to render configurations for an extension based on
        an arbitrary schema and config_declaration.yaml

        Args:
            schema_id : an arbitrary schema ID
            render_template (optional): a path to a render template
            breadcrum_label (optional): page breadcrumb label
            page_title (optional): page title
            success_update_message (optional): message text after a success update
            fields (optional): provide a schema fields list directly
        """
        self.schema_id = schema_id
        self.render_template = render_template
        self.breadcrum_label = breadcrum_label
        self.page_title = page_title
        self.success_update_message = success_update_message
        self.fields = fields

    def get(self):
        self.schema = self.get_config_schema()
        self.data = self.get_config_form_data()
        self.disable_non_editable_fields()

        return tk.render(
            self.render_template,
            self.prepare_extra_vars(self.schema, self.data, {}),
        )

    def get_config_schema(self) -> dict[str, Any]:
        """Fetch a full schema or use the fields user provides and put them inside
        a dict to imitate a schema"""
        schema = (
            tk.h.ap_get_arbitrary_schema(self.schema_id)
            if not self.fields
            else {"schema_id": self.schema_id, "fields": self.fields}
        )

        return schema

    def get_config_form_data(self) -> dict[str, Any]:
        """Fetch/humanize configuration values from a CKANConfig"""
        from ckanext.editable_config.shared import value_as_string

        data = {}

        for field in self.schema["fields"]:
            if field["field_name"] not in tk.config:
                continue

            data[field["field_name"]] = value_as_string(
                field["field_name"], tk.config[field["field_name"]]
            )

        return data

    def disable_non_editable_fields(self) -> None:
        """Update a schema fields and disable those, that are not marked as editable
        in a config_declaration.yml"""
        from ckanext.editable_config.shared import is_editable

        for field in self.schema["fields"]:
            if is_editable(field["field_name"]):
                continue

            field.setdefault("form_attrs", {})
            field["form_attrs"]["disabled"] = 1

    def prepare_extra_vars(
        self, schema: dict[str, Any], data: dict[str, Any], errors: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "data": data,
            "errors": errors,
            "schema": schema,
            "breadcrum_label": self.breadcrum_label,
            "page_title": self.page_title,
        }

    def post(self):
        self.schema = self.get_config_schema()
        self.data = parse_params(tk.request.form)
        self.disable_non_editable_fields()
        self.throw_away_undeclared_fields()

        try:
            if tk.request.form.get("reset"):
                tk.get_action("editable_config_reset")(
                    {},
                    {"keys": list(self.data)},
                )
            else:
                tk.get_action("editable_config_change")(
                    {},
                    {"options": self.data},
                )
        except tk.ValidationError as e:
            return tk.render(
                self.render_template,
                self.prepare_extra_vars(self.schema, self.data, e.error_dict),
            )

        tk.h.flash_success(self.success_update_message)

        return tk.redirect_to(tk.request.endpoint)

    def throw_away_undeclared_fields(self) -> None:
        self.data = {k: v for k, v in self.data.items() if k in tk.config}
