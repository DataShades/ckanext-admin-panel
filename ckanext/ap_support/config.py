from __future__ import annotations

import ckan.plugins.toolkit as tk

CONF_TICKET_CATEGORIES = "ckanext.admin_panel.support.category_list"
DEF_TICKET_CATEGORIES = ["Feature request", "Data request", "Bug report", "Other"]


def get_ticket_categories() -> list[str]:
    return tk.aslist(tk.config.get(CONF_TICKET_CATEGORIES) or DEF_TICKET_CATEGORIES)
