from __future__ import annotations

from typing import Any

from ckan import model

from ckanext.ap_support import config as support_config


def ap_support_get_category_options() -> list[dict[str, Any]]:
    return [
        {"value": category, "text": category}
        for category in support_config.get_ticket_categories()
    ]


def ap_support_get_sysadmins() -> list[dict[str, str]]:
    users = (
        model.Session.query(model.User)
        .filter(model.User.sysadmin.is_(True), model.User.state == model.State.ACTIVE)
        .order_by(model.User.name)
        .all()
    )

    return [{"value": u.id, "text": u.fullname or u.name} for u in users]
