from __future__ import annotations

import json
from functools import partial
from typing import Any, Callable, Union, cast

from flask import Blueprint, Response, jsonify, make_response
from flask.views import MethodView

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic import parse_params

import ckanext.ap_cron.utils as cron_utils
from ckanext.ap_cron import types as cron_types
from ckanext.ap_cron.interfaces import IAPCron
from ckanext.ap_cron.model import CronJob
from ckanext.collection.shared import get_collection

from ckanext.ap_main.utils import ap_before_request

ap_cron = Blueprint(
    "ap_cron",
    __name__,
    url_prefix="/admin-panel/cron",
)
ap_cron.before_request(ap_before_request)


class CronManagerView(MethodView):
    def get(self) -> Union[str, Response]:
        return tk.render(
            "ap_cron/cron_list.html",
            extra_vars={
                "collection": get_collection("ap-cron", parse_params(tk.request.args)),
            },
        )

    def post(self) -> Response:
        bulk_action = tk.request.form.get("bulk-action")
        entity_ids = tk.request.form.getlist("entity_id")

        action_func = self._get_bulk_action(bulk_action) if bulk_action else None

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("ap_cron.manage")

        for entity_id in entity_ids:
            try:
                action_func(entity_id)
            except tk.ValidationError as e:
                tk.h.flash_error(str(e))

        return tk.redirect_to("ap_cron.manage")

    def _get_bulk_action(self, value: str) -> Callable[[str], None] | None:
        return {
            "1": partial(self._change_job_state, state=CronJob.State.disabled),
            "2": partial(self._change_job_state, state=CronJob.State.active),
            "3": self._remove_job,
        }.get(value)

    def _change_job_state(self, job_id: str, state: str) -> None:
        tk.get_action("ap_cron_update_cron_job")(
            {"ignore_auth": True},
            {
                "id": job_id,
                "state": state,
            },
        )

    def _remove_job(self, job_id: str) -> None:
        tk.get_action("ap_cron_remove_cron_job")({"ignore_auth": True}, {"id": job_id})


class CronAddView(MethodView):
    def post(self) -> Response:
        data_dict, errors = self._prepare_payload()

        if errors:
            tk.h.flash_error(errors)
            return tk.redirect_to("ap_cron.manage")

        try:
            tk.get_action("ap_cron_add_cron_job")(
                {
                    "user": tk.current_user.name,
                    "auth_user_obj": tk.current_user,
                },
                cast(types.DataDict, data_dict),
            )
        except tk.ValidationError as e:
            tk.h.flash_error(e)
            return tk.redirect_to("ap_cron.manage")

        tk.h.flash_success(tk._("The cron job has been created!"))

        return tk.redirect_to("ap_cron.manage")

    def _prepare_payload(self) -> tuple[cron_types.CronJobData | None, dict[str, Any]]:
        errors = {}

        try:
            data = tk.request.form.get("data", "{}")
            data = json.loads(data)
        except ValueError:
            tk.h.flash_error(errors)
            errors["data"] = tk._("Cron job data must be a valid JSON")
            return None, errors

        result = cron_types.CronJobData(
            name=tk.request.form.get("name", ""),
            schedule=tk.request.form.get("schedule", ""),
            actions=tk.request.form.get("actions", ""),
            data=data,
            timeout=tk.request.form.get("timeout", ""),
        )

        return result, errors


class CronDeleteJobView(MethodView):
    def post(self, job_id: str) -> str:
        try:
            tk.get_action("ap_cron_remove_cron_job")(
                {},
                cast(types.DataDict, {"id": job_id}),
            )
        except tk.ValidationError:
            pass

        return ""


class CronRunJobView(MethodView):
    """Initially I wanted to make it with HTMX. Having a get endpoint for such
    an action is a bit wrong."""

    def get(self, job_id: str) -> Response:
        try:
            result = tk.get_action("ap_cron_run_cron_job")(
                {},
                cast(types.DataDict, {"id": job_id}),
            )
        except tk.ValidationError as e:
            tk.h.flash_error(e.error_dict["message"])
            return tk.redirect_to("ap_cron.manage")

        tk.h.flash_success(
            f"The cron job \"{result['job']['name']}\" has been started!"
        )
        return tk.redirect_to("ap_cron.manage")


class CronEditJobFormView(MethodView):
    def get(self, job_id: str) -> str:
        try:
            result = tk.get_action("ap_cron_get_cron_job")(
                {},
                cast(types.DataDict, {"id": job_id}),
            )
        except tk.ValidationError as e:
            tk.h.flash_error(e.error_dict)
            return ""

        return tk.render(
            "ap_cron/cron_edit_modal_form.html",
            extra_vars={"data": result, "scope": "edit"},
        )


class CronEditJobView(MethodView):
    def post(self) -> Response:
        try:
            result = tk.get_action("ap_cron_update_cron_job")(
                {},
                cast(types.DataDict, dict(tk.request.form)),
            )
        except tk.ValidationError as e:
            tk.h.flash_error(e.error_dict)
            return tk.redirect_to("ap_cron.manage")

        tk.h.flash_success(f"The cron job \"{result['name']}\" has been updated.")

        return tk.redirect_to("ap_cron.manage")


class CronRunActiveView(MethodView):
    """Schedule all the cron jobs that are not pending or running. The current
    cron job schedule will be ignored."""

    def post(self) -> Response:
        jobs_list = CronJob.get_list(
            states=[
                CronJob.State.failed,
                CronJob.State.finished,
                CronJob.State.active,
                CronJob.State.pending,
            ]
        )

        for job in jobs_list:
            cron_utils.enqueue_cron_job(job)

        tk.h.flash_success(
            f"All active cron jobs have been scheduled: {len(jobs_list)}."
        )

        return tk.redirect_to("ap_cron.manage")


def action_autocomplete() -> Response:
    """This is an autocomplete for a cron job actions. Cron job could work
    only with CKAN actions to prevent any non-wanted behaviour."""
    q = tk.request.args.get("incomplete", "")
    limit = tk.request.args.get("limit", 10)

    actions: list[dict[str, str]] = []

    if q:
        from ckan.logic import _actions

        for plugin in p.PluginImplementations(IAPCron):
            _actions = plugin.exclude_action(_actions)

        actions = [{"Name": action} for action in _actions if q in action][:limit]

    return make_response(jsonify({"ResultSet": {"Result": actions}}))


ap_cron.add_url_rule("/", view_func=CronManagerView.as_view("manage"))
ap_cron.add_url_rule("/add", view_func=CronAddView.as_view("add"))
ap_cron.add_url_rule("/delete/<job_id>", view_func=CronDeleteJobView.as_view("delete"))
ap_cron.add_url_rule("/run/<job_id>", view_func=CronRunJobView.as_view("run"))
ap_cron.add_url_rule(
    "/edit/<job_id>/get_form", view_func=CronEditJobFormView.as_view("get_edit_form")
)
ap_cron.add_url_rule("/edit", view_func=CronEditJobView.as_view("edit"))
ap_cron.add_url_rule("/run_active", view_func=CronRunActiveView.as_view("run_active"))

# API
ap_cron.add_url_rule("/actions_autocomplete", view_func=action_autocomplete)
