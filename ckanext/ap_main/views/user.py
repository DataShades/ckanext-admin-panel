from __future__ import annotations

import logging
from functools import partial
from typing import Any, TypeAlias

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.lib.navl.dictization_functions as df
import ckan.plugins.toolkit as tk
from ckan import logic, model, types

import ckanext.tables.shared as t
from ckanext.ap_main import formatters as f
from ckanext.ap_main.logic import schema as ap_schema
from ckanext.ap_main.utils import ap_before_request
from ckanext.tables.shared import GenericTableView

ContentList: TypeAlias = "list[dict[str, Any]]"

ap_user = Blueprint("ap_user", __name__, url_prefix="/admin-panel")
ap_user.before_request(ap_before_request)

log = logging.getLogger(__name__)


class UserTable(t.TableDefinition):
    def __init__(self):
        super().__init__(
            name="user",
            table_template="admin_panel/tables/table_base.html",
            data_source=t.DatabaseDataSource(
                stmt=model.Session.query(
                    model.User.id.label("id"),
                    model.User.name.label("name"),
                    model.User.fullname.label("fullname"),
                    model.User.email.label("email"),
                    model.User.state.label("state"),
                    model.User.sysadmin.label("sysadmin"),
                )
                .filter(model.User.name != tk.config["ckan.site_id"])
                .order_by(model.User.name)
            ),
            columns=[
                t.ColumnDefinition(
                    field="name",
                    formatters=[(f.UserLinkFormatter, {})],
                    tabulator_formatter="html",
                    min_width=300,
                ),
                t.ColumnDefinition(
                    field="fullname",
                    formatters=[(f.NoneAsEmptyFormatter, {})],
                    min_width=200,
                ),
                t.ColumnDefinition(
                    field="email",
                    formatters=[(f.NoneAsEmptyFormatter, {})],
                    min_width=200,
                ),
                t.ColumnDefinition(field="state", width=100, resizable=False),
                t.ColumnDefinition(
                    field="sysadmin",
                    formatters=[(f.BoolFormatter, {})],
                    width=120,
                    resizable=False,
                ),
            ],
            row_actions=[
                t.RowActionDefinition(
                    action="edit",
                    label="Edit",
                    icon="fa fa-pencil",
                    callback=lambda row: t.ActionHandlerResult(
                        success=True, redirect=tk.url_for("user.edit", id=row["id"])
                    ),
                ),
                t.RowActionDefinition(
                    action="view",
                    label="View",
                    icon="fa fa-eye",
                    callback=lambda row: t.ActionHandlerResult(
                        success=True, redirect=tk.url_for("user.read", id=row["id"])
                    ),
                ),
            ],
            bulk_actions=[
                t.BulkActionDefinition(
                    action="add_sysadmin",
                    label="Add sysadmin role to selected users",
                    callback=self._change_sysadmin_role,
                ),
                t.BulkActionDefinition(
                    action="remove_sysadmin",
                    label="Remove sysadmin role from selected users",
                    callback=partial(self._change_sysadmin_role, is_sysadmin=False),
                ),
                t.BulkActionDefinition(
                    action="block",
                    label="Block selected users",
                    callback=self._change_user_state,
                ),
                t.BulkActionDefinition(
                    action="unblock",
                    label="Unblock selected users",
                    callback=partial(self._change_user_state, is_active=True),
                ),
            ],
        )

    @staticmethod
    def _change_sysadmin_role(
        rows: list[t.Row], is_sysadmin: bool | None = True
    ) -> t.ActionHandlerResult:
        errors = []
        for row in rows:
            user = model.Session.query(model.User).get(row["id"])
            if not user:
                errors.append(f"User {row['name']} not found")
                continue

            user.sysadmin = is_sysadmin
            model.Session.commit()

        if errors:
            return t.ActionHandlerResult(success=False, error="\n".join(errors))

        return t.ActionHandlerResult(success=True)

    @staticmethod
    def _change_user_state(
        rows: list[t.Row], is_active: bool | None = False
    ) -> t.ActionHandlerResult:
        errors = []
        for row in rows:
            user = model.Session.query(model.User).get(row["id"])
            if not user:
                errors.append(f"User {row['name']} not found")
                continue

            user.state = model.State.ACTIVE if is_active else model.State.DELETED
            model.Session.commit()

        if errors:
            return t.ActionHandlerResult(success=False, error="\n".join(errors))

        return t.ActionHandlerResult(success=True)


class UserAddView(MethodView):
    def get(
        self,
        data: dict[str, Any] | None = None,
        errors: dict[str, Any] | None = None,
        error_summary: dict[str, Any] | None = None,
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
    view_func=GenericTableView.as_view(
        "list",
        table=UserTable,
        page_title="Users",
        breadcrumb_label="Users",
    ),
)
ap_user.add_url_rule("/user/add", view_func=UserAddView.as_view("create"))
