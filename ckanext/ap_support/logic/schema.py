from __future__ import annotations

from ckan import types
from ckan.logic.schema import validator_args

from ckanext.ap_support.model import Ticket


@validator_args
def ticket_create(
    not_missing: types.Validator,
    unicode_safe: types.Validator,
    user_id_or_name_exists: types.Validator,
    ap_support_category_validator: types.Validator,
) -> types.Schema:
    return {
        "subject": [not_missing, unicode_safe],
        "category": [not_missing, unicode_safe, ap_support_category_validator],
        "text": [not_missing, unicode_safe],
        "author_id": [not_missing, unicode_safe, user_id_or_name_exists],
    }


@validator_args
def ticket_show(
    ignore_missing: types.Validator,
    unicode_safe: types.Validator,
    ticket_id_exists: types.Validator,
) -> types.Schema:
    return {"id": [ignore_missing, unicode_safe, ticket_id_exists]}


@validator_args
def ticket_delete(
    ignore_missing: types.Validator,
    unicode_safe: types.Validator,
    ticket_id_exists: types.Validator,
) -> types.Schema:
    return {"id": [ignore_missing, unicode_safe, ticket_id_exists]}


@validator_args
def ticket_assign(
    not_missing: types.Validator,
    ignore_missing: types.Validator,
    ignore_empty: types.Validator,
    unicode_safe: types.Validator,
    ticket_id_exists: types.Validator,
    user_id_or_name_exists: types.Validator,
    boolean_validator: types.Validator,
) -> types.Schema:
    return {
        "id": [not_missing, unicode_safe, ticket_id_exists],
        "assignee_id": [
            ignore_missing,
            ignore_empty,
            unicode_safe,
            user_id_or_name_exists,
        ],
    }


@validator_args
def ticket_update(  # noqa: PLR0913
    not_missing: types.Validator,
    ignore_missing: types.Validator,
    unicode_safe: types.Validator,
    ignore: types.Validator,
    one_of: types.ValidatorFactory,
    ticket_id_exists: types.Validator,
) -> types.Schema:
    return {
        "id": [not_missing, unicode_safe, ticket_id_exists],
        "status": [
            ignore_missing,
            unicode_safe,
            one_of(
                [
                    Ticket.Status.opened,
                    Ticket.Status.closed,
                ]
            ),
        ],
        "text": [ignore_missing, unicode_safe],
        "__extras": [ignore],
        "__junk": [ignore],
    }


@validator_args
def message_create(
    not_missing: types.Validator,
    unicode_safe: types.Validator,
    user_id_or_name_exists: types.Validator,
    ticket_id_exists: types.Validator,
) -> types.Schema:
    return {
        "ticket_id": [not_missing, unicode_safe, ticket_id_exists],
        "author_id": [not_missing, unicode_safe, user_id_or_name_exists],
        "content": [not_missing, unicode_safe],
    }


@validator_args
def message_delete(
    not_missing: types.Validator,
    unicode_safe: types.Validator,
    message_id_exists: types.Validator,
) -> types.Schema:
    return {
        "id": [not_missing, unicode_safe, message_id_exists],
    }


@validator_args
def message_update(
    not_missing: types.Validator,
    unicode_safe: types.Validator,
    message_id_exists: types.Validator,
) -> types.Schema:
    return {
        "id": [not_missing, unicode_safe, message_id_exists],
        "content": [not_missing, unicode_safe],
    }
