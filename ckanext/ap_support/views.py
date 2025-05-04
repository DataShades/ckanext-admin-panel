from __future__ import annotations

from functools import partial
from typing import Callable, Union

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.logic import parse_params

from ckanext.ap_support.model import Ticket

from ckanext.ap_main.utils import ap_before_request

ap_support = Blueprint(
    "ap_support",
    __name__,
    url_prefix="/admin-panel/support",
)

ap_support.before_request(ap_before_request)


class SupportListView(MethodView):
    def get(self) -> Union[str, Response]:
        return tk.render(
            "ap_support/list.html",
            extra_vars={"collection": ""},
        )

    def post(self) -> Response:
        bulk_action = tk.request.form.get("bulk-action")
        entity_ids = tk.request.form.getlist("entity_id")

        action_func = self._get_bulk_action(bulk_action) if bulk_action else None

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("ap_support.list")

        for entity_id in entity_ids:
            try:
                if action_func(entity_id):
                    tk.h.flash_success(tk._("Done."))

            except tk.ValidationError as e:
                tk.h.flash_error(str(e))

        return tk.redirect_to("ap_support.list")

    def _get_bulk_action(self, value: str) -> Callable[[str], None] | None:
        return {
            "1": partial(self._change_ticket_state, status=Ticket.Status.closed),
            "2": partial(self._change_ticket_state, status=Ticket.Status.opened),
            "3": self._delete_ticket,
        }.get(value)

    def _change_ticket_state(self, ticket_id: str, status: str) -> bool:
        tk.get_action("ap_support_ticket_update")(
            {"ignore_auth": True},
            {
                "id": ticket_id,
                "status": status,
            },
        )

        return True

    def _delete_ticket(self, ticket_id: str) -> bool:
        tk.get_action("ap_support_ticket_delete")(
            {"ignore_auth": True},
            {"id": ticket_id},
        )

        return True


def init_modal():
    """This view inits the modal data on first open or after a submit"""

    return tk.render(
        "ap_support/ticket_modal_form.html",
    )


class AddTicketView(MethodView):
    def post(self):
        data_dict = parse_params(tk.request.form)
        data_dict["author_id"] = tk.g.userobj.id

        try:
            tk.get_action("ap_support_ticket_create")({"user": tk.g.user}, data_dict)
        except (tk.ObjectNotFound, tk.ValidationError) as e:
            return self._get_modal_body(
                title=tk._("An error occurred while creating the ticket"),
                message=str(e),
            )

        return self._get_modal_body(
            title=tk._("Your ticket has been successfully created"),
            message=tk._("View your tickets at the user account page"),
        )

    def _get_modal_body(self, title: str, message: str):
        return tk.render(
            "ap_support/ticket_modal_response.html",
            extra_vars={
                "title": title,
                "message": message,
            },
        )


class TicketReadView(MethodView):
    def get(self, ticket_id: str) -> str:
        try:
            ticket = tk.get_action("ap_support_ticket_show")(
                {"ignore_auth": True},
                {"id": ticket_id},
            )
        except tk.ValidationError:
            return tk.abort(404, tk._("Ticket not found"))

        return tk.render("ap_support/ticket_read.html", extra_vars={"ticket": ticket})


class TicketDeleteView(MethodView):
    def post(self, ticket_id: str) -> Response:
        tk.get_action("ap_support_ticket_delete")(
            {"ignore_auth": True},
            {"id": ticket_id},
        )

        tk.h.flash_success(tk._("The ticket has been deleted"))

        return tk.redirect_to("ap_support.list")


ap_support.add_url_rule("/", view_func=SupportListView.as_view("list"))
ap_support.add_url_rule(
    "/ticket/<ticket_id>", view_func=TicketReadView.as_view("ticket_read")
)
ap_support.add_url_rule(
    "/ticket/<ticket_id>/delete", view_func=TicketDeleteView.as_view("ticket_delete")
)

# HTMX
ap_support.add_url_rule("/init_modal", view_func=init_modal)
ap_support.add_url_rule(
    "/add_ticket", view_func=AddTicketView.as_view("add_ticket"), methods=("POST",)
)
