from __future__ import annotations

from cron_descriptor import get_description

import ckan.plugins.toolkit as tk

from ckanext.ap_cron import config as cron_conf
from ckanext.ap_cron import const as cron_const
from ckanext.ap_cron.model import CronJob
from ckanext.ap_cron.types import DictizedCronJob
from ckanext.toolbelt.decorators import Collector

helper, get_helpers = Collector("ap_cron").split()


@helper
def get_actions_list_options() -> list[dict[str, str]]:
    from ckan.logic import _actions

    return [{"value": action, "text": action} for action in sorted(_actions)]


@helper
def get_job_timeout() -> int:
    return cron_conf.get_job_timeout()


@helper
def explain_cron_schedule(schedule: str) -> str:
    non_standard = {
        "@reboot": tk._("At CKAN startup"),
        "@hourly": tk._("Every hour"),
        "@daily": tk._("Every day"),
        "@weekly": tk._("Every week"),
        "@monthly": tk._("Every month"),
        "@yearly": tk._("Every year"),
    }

    if explanation := non_standard.get(schedule):
        return explanation

    return get_description(schedule)


@helper
def is_job_running(job_data: DictizedCronJob) -> bool:
    return job_data["state"] in [CronJob.State.running, CronJob.State.pending]


@helper
def get_cron_logger_name() -> str:
    return cron_const.LOG_NAME
