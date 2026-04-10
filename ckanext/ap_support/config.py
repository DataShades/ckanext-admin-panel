from __future__ import annotations

import ckan.plugins.toolkit as tk

CONF_TICKET_CATEGORIES = "ckanext.admin_panel.support.category_list"
DEF_TICKET_CATEGORIES = ["Feature request", "Data request", "Bug report", "Other"]

CONF_NOTIFY_NEW_TICKET = "ckanext.admin_panel.support.notify_on_new_ticket"
CONF_NOTIFY_NEW_MESSAGE = "ckanext.admin_panel.support.notify_on_new_message"
CONF_NOTIFY_TICKET_UPDATE = "ckanext.admin_panel.support.notify_on_ticket_update"


def get_ticket_categories() -> list[str]:
    return tk.aslist(tk.config.get(CONF_TICKET_CATEGORIES) or DEF_TICKET_CATEGORIES)


def get_notify_on_new_ticket() -> bool:
    return tk.asbool(tk.config.get(CONF_NOTIFY_NEW_TICKET, True))


def get_notify_on_new_message() -> bool:
    return tk.asbool(tk.config.get(CONF_NOTIFY_NEW_MESSAGE, True))


def get_notify_on_ticket_update() -> bool:
    return tk.asbool(tk.config.get(CONF_NOTIFY_TICKET_UPDATE, True))
