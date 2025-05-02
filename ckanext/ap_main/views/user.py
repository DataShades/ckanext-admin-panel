from __future__ import annotations

import logging
from functools import partial
from typing import Any, Callable, Optional, Union

from flask import Blueprint, Response
from flask.views import MethodView
from typing_extensions import TypeAlias

import ckan.lib.navl.dictization_functions as df
import ckan.logic as logic
import ckan.plugins.toolkit as tk
from ckan import model, types

from ckanext.collection.shared import get_collection

from ckanext.ap_main.logic import schema as ap_schema
from ckanext.ap_main.utils import ap_before_request

UserList: TypeAlias = "list[dict[str, Any]]"

ap_user = Blueprint("ap_user", __name__, url_prefix="/admin-panel")
ap_user.before_request(ap_before_request)

log = logging.getLogger(__name__)


class UserListView(MethodView):
    def get(self) -> Union[str, Response]:
        return tk.render(
            "admin_panel/config/user/user_list.html", self._prepare_data_dict()
        )

    def _prepare_data_dict(self) -> dict[str, Any]:
        return {
            "collection": get_collection(
                "ap-user", logic.parse_params(tk.request.args)
            ),
        }

    def post(self) -> Response:
        bulk_action = tk.request.form.get("bulk-action")
        user_ids = tk.request.form.getlist("entity_id")

        if not bulk_action or not user_ids:
            return tk.redirect_to("ap_user.list")

        action_func = self._get_bulk_action(bulk_action)

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("ap_user.list")

        action_func(user_ids)

        tk.h.flash_success(tk._("Done."))

        return tk.redirect_to("ap_user.list")

    def _get_bulk_action(self, value: str) -> Callable[[list[str]], None] | None:
        return {
            "1": partial(self._change_user_role, is_sysadmin=True),
            "2": partial(self._change_user_role, is_sysadmin=False),
            "3": partial(self._change_user_state, is_active=False),
            "4": partial(self._change_user_state, is_active=True),
        }.get(value)

    @staticmethod
    def _change_user_role(
        user_ids: list[str], is_sysadmin: Optional[bool] = False
    ) -> None:
        for user_id in user_ids:
            try:
                logic.get_action("user_patch")(
                    {"ignore_auth": True}, {"id": user_id, "sysadmin": is_sysadmin}
                )
            except tk.ObjectNotFound:
                pass

    @staticmethod
    def _change_user_state(
        user_ids: list[str], is_active: Optional[bool] = False
    ) -> None:
        state = model.State.ACTIVE if is_active else model.State.DELETED

        for user_id in user_ids:
            try:
                logic.get_action("user_patch")(
                    {"ignore_auth": True},
                    {"id": user_id, "state": state},
                )
            except tk.ObjectNotFound:
                pass
            except tk.ValidationError:
                # we shouldn't get there, but currently CKAN has a problem
                # system user doesn't have an email, so it's impossible to update it
                pass


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


ap_user.add_url_rule("/user/list", view_func=UserListView.as_view("list"))
ap_user.add_url_rule("/user/add", view_func=UserAddView.as_view("create"))
