from __future__ import annotations

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.logic import parse_params

from ckanext.ap_main.utils import ap_before_request
from ckanext.ap_support.table import SupportTable, UserTicketTable
from ckanext.tables.shared import GenericTableView

ap_support = Blueprint(
    "ap_support",
    __name__,
    url_prefix="/admin-panel/support",
)

ap_support.before_request(ap_before_request)


def init_modal():
    """This view inits the modal data on first open or after a submit."""
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


class AddMessageView(MethodView):
    def post(self, ticket_id: str):
        data_dict = parse_params(tk.request.form)

        try:
            message = tk.get_action("ap_support_message_create")({"user": tk.g.user}, {
                "ticket_id": ticket_id,
                "author_id": tk.current_user.id,
                "content": data_dict.get("content", ""),
            })
        except (tk.ObjectNotFound, tk.ValidationError) as e:
            return tk.render(
                "ap_support/ticket_modal_response.html",
                extra_vars={
                    "title": tk._("Error adding message"),
                    "message": str(e),
                },
            )

        ticket = tk.get_action("ap_support_ticket_show")(
            {"ignore_auth": True}, {"id": ticket_id}
        )

        return tk.render(
            "ap_support/messages_container.html",
            extra_vars={"ticket": ticket},
        )


class DeleteMessageView(MethodView):
    def post(self, message_id: str) -> Response:
        try:
            tk.get_action("ap_support_message_delete")(
                {"user": tk.g.user},
                {"id": message_id},
            )
        except (tk.ObjectNotFound, tk.ValidationError, tk.NotAuthorized) as e:
            tk.h.flash_error(str(e))
            return Response("", status=400)

        # Return empty response for HTMX to remove the element
        return Response("", status=200)


class UpdateMessageView(MethodView):
    def post(self, message_id: str):
        data_dict = parse_params(tk.request.form)
        data_dict["id"] = message_id

        try:
            tk.get_action("ap_support_message_update")(
                {"user": tk.g.user},
                data_dict,
            )
        except (tk.ObjectNotFound, tk.ValidationError, tk.NotAuthorized) as e:
            return tk.render(
                "ap_support/ticket_modal_response.html",
                extra_vars={
                    "title": tk._("Error updating message"),
                    "message": str(e),
                },
            )

        ticket = tk.get_action("ap_support_ticket_show")(
            {"ignore_auth": True},
            {"id": data_dict.get("ticket_id")},
        )

        for msg in ticket.get("messages", []):
            if msg["id"] != int(message_id):
                continue

            return tk.render(
                "ap_support/message_item.html",
                extra_vars={"message": msg, "ticket": ticket},
            )

        return ""


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


class TicketUpdateStatusView(MethodView):
    def post(self, ticket_id: str) -> Response:
        try:
            ticket = tk.get_action("ap_support_ticket_show")(
                {"ignore_auth": True}, {"id": ticket_id}
            )
            new_status = (
                "closed"
                if ticket["status"] == "opened"
                else "opened"
            )
            tk.get_action("ap_support_ticket_update")(
                {"user": tk.g.user},
                {"id": ticket_id, "status": new_status},
            )
        except (tk.ObjectNotFound, tk.ValidationError, tk.NotAuthorized) as e:
            tk.h.flash_error(str(e))
            return Response("", status=400)

        redirect_url = tk.url_for("ap_support.ticket_read", ticket_id=ticket_id)

        if tk.request.headers.get("HX-Request"):
            return Response("", status=200, headers={"HX-Redirect": redirect_url})

        return tk.redirect_to(redirect_url)


class TicketDeleteView(MethodView):
    def post(self, ticket_id: str) -> Response:
        tk.get_action("ap_support_ticket_delete")(
            {"ignore_auth": True},
            {"id": ticket_id},
        )

        tk.h.flash_success(tk._("The ticket has been deleted"))

        redirect_url = tk.url_for("ap_support.list")

        if tk.request.headers.get("HX-Request"):
            return Response("", status=200, headers={"HX-Redirect": redirect_url})

        return tk.redirect_to(redirect_url)


ap_support.add_url_rule(
    "/", view_func=GenericTableView.as_view("list", table=SupportTable)
)
ap_support.add_url_rule(
    "/my-tickets",
    view_func=GenericTableView.as_view("my_tickets", table=UserTicketTable),
)
ap_support.add_url_rule(
    "/ticket/<ticket_id>", view_func=TicketReadView.as_view("ticket_read")
)
ap_support.add_url_rule(
    "/ticket/<ticket_id>/update-status",
    view_func=TicketUpdateStatusView.as_view("ticket_update_status"),
    methods=("POST",),
)
ap_support.add_url_rule(
    "/ticket/<ticket_id>/delete", view_func=TicketDeleteView.as_view("ticket_delete")
)
ap_support.add_url_rule(
    "/ticket/<ticket_id>/message", view_func=AddMessageView.as_view("add_message")
)
ap_support.add_url_rule(
    "/message/<message_id>/delete",
    view_func=DeleteMessageView.as_view("delete_message"),
    methods=("POST",),
)
ap_support.add_url_rule(
    "/message/<message_id>/update",
    view_func=UpdateMessageView.as_view("update_message"),
    methods=("POST",),
)

# HTMX
ap_support.add_url_rule("/init_modal", view_func=init_modal)
ap_support.add_url_rule(
    "/add_ticket", view_func=AddTicketView.as_view("add_ticket"), methods=("POST",)
)
