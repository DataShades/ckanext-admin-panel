from __future__ import annotations

import json

from typing import Any, Union, cast
from ckan import types

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.lib.helpers import Page

from ckanext.ap_main.utils import ap_before_request
from ckanext.ap_cron import types as cron_types

ap_cron = Blueprint("ap_cron", __name__, url_prefix="/admin-panel")
ap_cron.before_request(ap_before_request)


class CronManagerView(MethodView):
    def get(self) -> Union[str, Response]:
        return tk.render(
            "ap_cron/cron_list.html",
            extra_vars=self._prepare_data_dict(),
        )

    def _prepare_data_dict(self) -> dict[str, Any]:
        self.q = tk.request.args.get("q", "").strip()
        self.order_by = tk.request.args.get("order_by", "name")
        self.sort = tk.request.args.get("sort", "desc")

        cron_jobs = tk.get_action("ap_cron_get_cron_job_list")({}, {})

        cron_jobs = self._search_items(cron_jobs)
        cron_jobs = self._sort_items(cron_jobs)

        return {
            "page": self._get_pager(cron_jobs),
            "columns": self._get_table_columns(),
            "q": self.q,
            "order_by": self.order_by,
            "sort": self.sort,
            "bulk_options": self._get_bulk_action_options(),
        }

    def _search_items(self, item_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.q:
            return item_list

        return [item for item in item_list if self.q.lower() in item["name"].lower()]

    def _sort_items(self, item_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.order_by = tk.request.args.get("order_by", "timestamp")
        self.sort = tk.request.args.get("sort", "desc")

        return sorted(
            item_list,
            key=lambda x: x.get(self.order_by, ""),
            reverse=self.sort == "desc",
        )

    def _get_pager(self, cron_jobs: list[dict[str, Any]]) -> Page:
        page_number = tk.h.get_page_number(tk.request.args)
        default_limit: int = tk.config.get("ckan.user_list_limit")
        limit = int(tk.request.args.get("limit", default_limit))

        return Page(
            collection=cron_jobs,
            page=page_number,
            url=tk.h.pager_url,
            item_count=len(cron_jobs),
            items_per_page=limit,
        )

    def _get_table_columns(self) -> list[dict[str, Any]]:
        return [
            tk.h.ap_table_column("name", width="20%"),
            tk.h.ap_table_column("actions", width="20%"),
            tk.h.ap_table_column(
                "data",
                column_renderer="ap_cron_json_display",
                width="20%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "schedule",
                column_renderer="ap_cron_schedule",
                width="10%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "last_run",
                label="Last run",
                column_renderer="ap_cron_last_run",
                width="5%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "state",
                label="State",
                width="5%",
                sortable=False,
            ),
            tk.h.ap_table_column(
                "actions",
                column_renderer="ap_action_render",
                width="20%",
                sortable=False,
                actions=[
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        label=tk._("Logs"),
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "edit",
                        },
                        attributes={"class": "btn btn-black"},
                    ),
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        label=tk._("Edit"),
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "edit",
                        },
                    ),
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        icon="fa fa-play",
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "read",
                        },
                    ),
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        icon="fa fa-stop",
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "read",
                        },
                        attributes={"class": "btn btn-danger"},
                    ),
                    tk.h.ap_table_action(
                        "ap_content.entity_proxy",
                        icon="fa fa-trash-alt",
                        params={
                            "entity_id": "$id",
                            "entity_type": "$type",
                            "view": "read",
                        },
                        attributes={
                            "class": "btn btn-danger",
                            "hx-trigger": "click",
                            "hx-post": lambda item: tk.h.url_for(
                                "ap_cron.delete", job_id=item["id"]
                            ),
                        },
                    ),
                ],
            ),
        ]

    #                 <button
    #     class="remove-step btn btn-danger"
    #     data-step-id="{{ step_id }}"
    #     hx-trigger="click"
    #     hx-post="{{ h.url_for('tour.delete_step', tour_step_id=step_id) }}"
    #     >
    #     {{ _("Delete") }}
    # </button>

    def _get_bulk_action_options(self):
        return [
            {
                "value": "1",
                "text": tk._("Disable selected job"),
            },
            {
                "value": "2",
                "text": tk._("Enable selected job"),
            },
            {
                "value": "3",
                "text": tk._("Delete selected job"),
            },
        ]


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
            data = tk.request.form.get("job_data", "{}")
            data = json.loads(data)
        except ValueError:
            tk.h.flash_error(errors)
            errors["data"] = tk._("Cron job data must be a valid JSON")
            return None, errors

        result = cron_types.CronJobData(
            name=tk.request.form.get("job_name", ""),
            schedule=tk.request.form.get("job_schedule", ""),
            actions=tk.request.form.get("job_action", ""),
            data={"kwargs": data},
            timeout=tk.request.form.get("job_timeout", ""),
        )

        return result, errors


class CronDeleteView(MethodView):
    def post(self, job_id: str) -> str:
        try:
            tk.get_action("ap_cron_remove_cron_job")(
                {},
                cast(types.DataDict, {"id": job_id}),
            )
        except tk.ValidationError as e:
            pass

        return ""


ap_cron.add_url_rule("/reports/cron", view_func=CronManagerView.as_view("manage"))
ap_cron.add_url_rule("/reports/cron/add", view_func=CronAddView.as_view("add"))
ap_cron.add_url_rule(
    "/reports/cron/delete/<job_id>", view_func=CronDeleteView.as_view("delete")
)
