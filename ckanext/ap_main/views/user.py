from __future__ import annotations

import logging
from functools import partial
from typing import Any, Optional

from flask import Blueprint, Response
from flask.views import MethodView
from typing_extensions import TypeAlias

import ckan.lib.navl.dictization_functions as df
import ckan.logic as logic
import ckan.plugins.toolkit as tk
from ckan import model, types

import ckanext.ap_main.table as table
import ckanext.ap_main.types as ap_types
from ckanext.ap_main.logic import schema as ap_schema
from ckanext.ap_main.utils import ap_before_request
from ckanext.ap_main.views.generics import ApTableView

UserList: TypeAlias = "list[dict[str, Any]]"
ContentList: TypeAlias = "list[dict[str, Any]]"

ap_user = Blueprint("ap_user", __name__, url_prefix="/admin-panel")
ap_user.before_request(ap_before_request)

log = logging.getLogger(__name__)


class UserTable(table.TableDefinition):
    def __init__(self):
        super().__init__(
            name="user",
            ajax_url=tk.url_for("ap_user.list", data=True),
            placeholder=tk._("No users found"),
            columns=[
                table.ColumnDefinition("id", visible=False, filterable=False),
                table.ColumnDefinition(
                    "name",
                    formatters=[("user_link", {})],
                    tabulator_formatter="html",
                    min_width=300,
                ),
                table.ColumnDefinition(
                    "fullname",
                    formatters=[("none_as_empty", {})],
                    min_width=200,
                ),
                table.ColumnDefinition(
                    "email",
                    formatters=[("none_as_empty", {})],
                    min_width=200,
                ),
                table.ColumnDefinition("state"),
                table.ColumnDefinition("sysadmin", formatters=[("bool", {})]),
                table.ColumnDefinition(
                    "actions",
                    formatters=[("actions", {})],
                    filterable=False,
                    tabulator_formatter="html",
                    sorter=None,
                    resizable=False,
                ),
            ],
            actions=[
                table.ActionDefinition(
                    "edit",
                    icon="fa fa-pencil",
                    endpoint="user.edit",
                    url_params={"id": "$id"},
                ),
                table.ActionDefinition(
                    "view",
                    icon="fa fa-eye",
                    endpoint="user.read",
                    url_params={"id": "$id"},
                ),
            ],
            global_actions=[
                table.GlobalActionDefinition(
                    action="add_sysadmin", label="Add sysadmin role to selected users"
                ),
                table.GlobalActionDefinition(
                    action="remove_sysadmin",
                    label="Remove sysadmin role from selected users",
                ),
                table.GlobalActionDefinition(
                    action="block", label="Block selected users"
                ),
                table.GlobalActionDefinition(
                    action="unblock", label="Unblock selected users"
                ),
            ],
        )

    def get_raw_data(self) -> list[dict[str, Any]]:
        query = (
            model.Session.query(
                model.User.id.label("id"),
                model.User.name.label("name"),
                model.User.fullname.label("fullname"),
                model.User.email.label("email"),
                model.User.state.label("state"),
                model.User.sysadmin.label("sysadmin"),
            )
            .filter(model.User.name != tk.config["ckan.site_id"])
            .order_by(model.User.name)
        )

        columns = ["id", "name", "fullname", "email", "state", "sysadmin"]

        return [dict(zip(columns, row)) for row in query.all()]


class UserListView(ApTableView):
    def get_global_action(self, value: str) -> ap_types.GlobalActionHandler | None:
        return {
            "add_sysadmin": self._change_sysadmin_role,
            "remove_sysadmin": partial(self._change_sysadmin_role, is_sysadmin=False),
            "block": self._change_user_state,
            "unblock": partial(self._change_user_state, is_active=True),
        }.get(value)

    @staticmethod
    def _change_sysadmin_role(
        row: ap_types.Row, is_sysadmin: Optional[bool] = True
    ) -> ap_types.GlobalActionHandlerResult:
        user = model.Session.query(model.User).get(row["id"])
        if not user:
            return False, "User not found"

        user.sysadmin = is_sysadmin
        model.Session.commit()
        return True, None

    @staticmethod
    def _change_user_state(
        row: ap_types.Row, is_active: Optional[bool] = False
    ) -> ap_types.GlobalActionHandlerResult:
        user = model.Session.query(model.User).get(row["id"])
        if not user:
            return False, "User not found"

        user.state = model.State.ACTIVE if is_active else model.State.DELETED
        model.Session.commit()
        return True, None


class UserAddView(MethodView):
    def get(
        self,
        data: Optional[dict[str, Any]] = None,
        errors: Optional[dict[str, Any]] = None,
        error_summary: Optional[dict[str, Any]] = None,
    ) -> str:
        return tk.render(
            "admin_panel/config/user/create_form.html",
            extra_vars={
                "data": data or {},
                "errors": errors or {},
                "error_summary": error_summary or {},
            },
        )

    def post(self) -> str | Response:
        context = self._make_context()

        try:
            data_dict = self._parse_payload()
        except df.DataError:
            tk.abort(400, tk._("Integrity Error"))

        try:
            user_dict = logic.get_action("user_create")(context, data_dict)
        except logic.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(data_dict, errors, error_summary)

        if data_dict.get("role") == "sysadmin":
            self._make_user_sysadmin(user_dict)

        link = (
            tk.h.literal(f"<a href='{tk.url_for('user.read', id=user_dict['name'])}'>")
            + user_dict["name"]
            + tk.h.literal("</a>")
        )
        tk.h.flash_success(
            tk._(f"Created a new user account for {link}"), allow_html=True
        )
        log.info(tk._(f"Created a new user account for {link}"))

        return tk.redirect_to("ap_user.create")

    def _make_context(self) -> types.Context:
        context: types.Context = {
            "user": tk.current_user.name,
            "auth_user_obj": tk.current_user,
            "schema": ap_schema.ap_user_new_form_schema(),
            "save": "save" in tk.request.form,
        }

        return context

    def _parse_payload(self) -> dict[str, Any]:
        data_dict = logic.clean_dict(
            df.unflatten(logic.tuplize_dict(logic.parse_params(tk.request.form)))
        )

        data_dict.update(
            logic.clean_dict(
                df.unflatten(logic.tuplize_dict(logic.parse_params(tk.request.files)))
            )
        )

        return data_dict

    def _make_user_sysadmin(self, user_dict: dict[str, Any]) -> None:
        try:
            logic.get_action("user_patch")(
                {"ignore_auth": True}, {"id": user_dict["id"], "sysadmin": True}
            )
        except tk.ObjectNotFound:
            pass


ap_user.add_url_rule(
    "/user",
    view_func=UserListView.as_view(
        "list", table=UserTable, breadcrumb_label="Users", page_title="Users"
    ),
)
ap_user.add_url_rule("/user/add", view_func=UserAddView.as_view("create"))
