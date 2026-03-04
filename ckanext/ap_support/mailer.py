import logging
from typing import Any

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.lib import mailer

from ckanext.ap_support import config
from ckanext.ap_support.types import DictizedMessage, DictizedTicket

log = logging.getLogger(__name__)


def notify_admins_on_new_ticket(sender: None, **kwargs: Any) -> None:
    """Notify sysadmins (and the assignee if set) when a ticket is created.

    Subscribed to: ``ap_support:ticket_created``

    Kwargs:
        ticket (DictizedTicket): the newly created ticket.
    """
    if not config.get_notify_on_new_ticket():
        return

    ticket: DictizedTicket = kwargs["ticket"]

    recipients = _get_sysadmin_users()

    if ticket.get("assignee"):
        assignee = model.User.get(ticket["assignee"]["id"])
        if assignee and assignee not in recipients:
            recipients.append(assignee)

    for user in recipients:
        log.info(
            "[ap_support] Notifying %s about new ticket #%s: %r",
            user.name,
            ticket["id"],
            ticket["subject"],
        )

        mailer.mail_user(
            user,
            subject=f"New support ticket: {ticket['subject']}",
            body=_render_new_ticket(ticket, recipient_name=user.display_name),
        )


def notify_author_on_new_message(sender: None, **kwargs: Any) -> None:
    """Notify the ticket author when someone else posts a message.

    Subscribed to: ``ap_support:message_created``

    Kwargs:
        ticket (DictizedTicket): the parent ticket.
        message (DictizedMessage): the newly created message.
    """
    if not config.get_notify_on_new_message():
        return

    ticket: DictizedTicket = kwargs["ticket"]
    message: DictizedMessage = kwargs["message"]

    # Don't send a notification when the author is replying to themselves.
    if message["author"]["id"] == ticket["author"]["id"]:
        return

    author = model.User.get(ticket["author"]["id"])
    if not author:
        log.warning(
            "[ap_support] Ticket #%s author not found, skipping notification",
            ticket["id"],
        )
        return

    log.info(
        "[ap_support] Notifying %s about new message on ticket #%s",
        author.name,
        ticket["id"],
    )

    mailer.mail_user(
        author,
        subject=f"New reply on your ticket: {ticket['subject']}",
        body=_render_new_message(ticket, message, recipient_name=author.display_name),
    )


def notify_author_on_ticket_update(sender: None, **kwargs: Any) -> None:
    """Notify the ticket author when the ticket is updated.

    Subscribed to: ``ap_support:ticket_updated``

    Kwargs:
        ticket (DictizedTicket): the updated ticket.
    """
    if not config.get_notify_on_ticket_update():
        return

    ticket: DictizedTicket = kwargs["ticket"]

    author = model.User.get(ticket["author"]["id"])
    if not author:
        log.warning(
            "[ap_support] Ticket #%s author not found, skipping notification",
            ticket["id"],
        )
        return

    log.info(
        "[ap_support] Notifying %s about updated ticket #%s",
        author.name,
        ticket["id"],
    )

    mailer.mail_user(
        author,
        subject=f"Ticket updated: {ticket['subject']}",
        body=_render_ticket_updated(ticket, recipient_name=author.display_name),
    )


def _get_sysadmin_users() -> list[model.User]:
    """Return all active sysadmin users."""
    return (
        model.Session.query(model.User)
        .filter(model.User.sysadmin.is_(True))
        .filter(model.User.state == model.State.ACTIVE)
        .filter(model.User.email.isnot(None))
        .all()
    )


def _render_new_ticket(ticket: DictizedTicket, recipient_name: str) -> str:
    return tk.render(
        "ap_support/emails/new_ticket.txt",
        extra_vars={
            **_base_vars(ticket),
            "ticket": ticket,
            "recipient_name": recipient_name,
        },
    )


def _render_new_message(
    ticket: DictizedTicket, message: DictizedMessage, recipient_name: str
) -> str:
    return tk.render(
        "ap_support/emails/new_message.txt",
        extra_vars={
            **_base_vars(ticket),
            "ticket": ticket,
            "message": message,
            "recipient_name": recipient_name,
        },
    )


def _render_ticket_updated(ticket: DictizedTicket, recipient_name: str) -> str:
    return tk.render(
        "ap_support/emails/ticket_updated.txt",
        extra_vars={
            **_base_vars(ticket),
            "ticket": ticket,
            "recipient_name": recipient_name,
        },
    )


def _base_vars(ticket: DictizedTicket) -> dict:
    """Build the common template context for all support emails."""
    site_url = tk.config.get("ckan.site_url", "")

    return {
        "site_title": tk.config.get("ckan.site_title", "CKAN"),
        "site_url": site_url,
        "ticket_url": site_url.rstrip("/")
        + tk.url_for("ap_support.ticket_read", ticket_id=ticket["id"]),
    }
