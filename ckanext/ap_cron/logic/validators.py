from __future__ import annotations

from typing import Any

from croniter import croniter

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic import get_action

from ckanext.ap_cron import model as cron_model
from ckanext.ap_cron.const import KWARGS
from ckanext.ap_cron.interfaces import IAPCron


def cron_schedule_validator(value: str, context: types.Context) -> Any:
    """Ensures that the cron schedule has valid format"""
    result = croniter.is_valid(value)

    if value == "@reboot":
        result = True
    elif len(value.split()) == 6:
        # We don't support spring schedule format
        result = False
    else:
        result = croniter.is_valid(value)

    if not result:
        raise tk.Invalid(tk._("The cron schedule is not properly formed."))

    return value


def cron_job_exists(job_id: str, context: types.Context) -> Any:
    """Ensures that the cron job with a given id exists."""

    session = context["session"]

    if not session.get(cron_model.CronJob, job_id):
        raise tk.Invalid("The cron job not found.")

    return job_id


def cron_action_exists(actions: list[str], context: types.Context) -> Any:
    """Check if all the actions are registered in CKAN"""
    action_funcs: dict[str, types.Action] = {}

    for action in actions:
        try:
            action_fn = get_action(action)
        except KeyError as e:
            raise tk.Invalid(str(e))

        action_funcs[action] = action_fn

    users_actions = list(action_funcs.keys())

    for plugin in p.PluginImplementations(IAPCron):
        action_funcs = plugin.exclude_action(action_funcs)

    for user_action in users_actions:
        if user_action not in action_funcs:
            raise tk.Invalid(
                f"Action {user_action} is excluded from usage in a cron job"
            )

    return actions


def cron_actions_to_string(actions: list[str], context: types.Context) -> str:
    return ", ".join(actions)


def cron_kwargs_provided(
    data: dict[str, Any], context: types.Context
) -> dict[str, Any]:
    if KWARGS not in data:
        raise tk.Invalid("The cron job data must contain `kwargs` dictionary.")

    return data
