from __future__ import annotations

import logging

from ckan import types
from ckan.logic import validate
from ckan.plugins import toolkit as tk

import ckanext.ap_support.logic.schema as schema
import ckanext.ap_support.model as support_model
from ckanext.ap_support.types import DictizedTicket

log = logging.getLogger(__name__)


@tk.side_effect_free
@validate(schema.ticket_search)
def ap_support_ticket_search(
    context: types.Context, data_dict: types.DataDict
) -> list[DictizedTicket]:
    tk.check_access("ap_support_ticket_search", context, data_dict)

    if data_dict.get("state"):
        result = support_model.Ticket.get_list(states=[data_dict["state"]])
    else:
        result = support_model.Ticket.get_list()

    return [ticket.dictize(context) for ticket in result]


@validate(schema.ticket_create)
def ap_support_ticket_create(
    context: types.Context, data_dict: types.DataDict
) -> DictizedTicket:
    tk.check_access("ap_support_ticket_create", context, data_dict)

    ticket = support_model.Ticket.add(data_dict)

    log.info("[id:%s] the ticket has been submitted", ticket["id"])

    return ticket


@tk.side_effect_free
@validate(schema.ticket_show)
def ap_support_ticket_show(
    context: types.Context, data_dict: types.DataDict
) -> DictizedTicket:
    tk.check_access("ap_support_ticket_show", context, data_dict)

    return support_model.Ticket.get(data_dict["id"]).dictize(context)


@tk.side_effect_free
@validate(schema.ticket_delete)
def ap_support_ticket_delete(
    context: types.Context, data_dict: types.DataDict
) -> DictizedTicket:
    tk.check_access("ap_support_ticket_delete", context, data_dict)

    ticket = support_model.Ticket.get(data_dict["id"])

    ticket.delete()

    context["session"].commit()

    return True


@tk.side_effect_free
@validate(schema.ticket_update)
def ap_support_ticket_update(
    context: types.Context, data_dict: types.DataDict
) -> DictizedTicket:
    tk.check_access("ap_support_ticket_delete", context, data_dict)

    ticket = support_model.Ticket.get(data_dict["id"])

    for key, value in data_dict.items():
        setattr(ticket, key, value)

    context["session"].commit()

    log.info("[id:%s] ticket been updated: %s", ticket.id, data_dict)

    return True
