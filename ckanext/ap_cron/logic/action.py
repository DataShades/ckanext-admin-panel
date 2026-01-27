from __future__ import annotations

import logging
from datetime import datetime as dt
from typing import Any, cast

from ckan import model, types
from ckan.logic import validate
from ckan.plugins import toolkit as tk

import ckanext.ap_cron.logic.schema as cron_schema
from ckanext.ap_cron.const import LOG_NAME
from ckanext.ap_cron.model import CronJob
from ckanext.ap_cron.types import CronJobData, DictizedCronJob
from ckanext.ap_cron.utils import enqueue_cron_job

log = logging.getLogger(LOG_NAME)


@validate(cron_schema.add_cron_job)
def ap_cron_add_cron_job(
    context: types.Context, data_dict: types.DataDict
) -> DictizedCronJob:
    tk.check_access("ap_cron_add_job", context, data_dict)

    job = CronJob.add(CronJobData(**data_dict))

    log.info("[id:%s] Cron job has been created", job.id)

    return job.dictize(context)


@tk.side_effect_free
@validate(cron_schema.get_cron_job)
def ap_cron_get_cron_job(
    context: types.Context, data_dict: types.DataDict
) -> DictizedCronJob:
    tk.check_access("ap_cron_get_job", context, data_dict)

    return cast(CronJob, CronJob.get(data_dict["id"])).dictize(context)


@validate(cron_schema.remove_cron_job)
def ap_cron_remove_cron_job(context: types.Context, data_dict: types.DataDict) -> bool:
    tk.check_access("ap_cron_remove_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))
    job.delete()

    model.Session.commit()

    log.info("[id:%s] Cron job has been removed", job.id)

    return True


@tk.side_effect_free
@validate(cron_schema.get_cron_job_list)
def ap_cron_get_cron_job_list(
    context: types.Context, data_dict: types.DataDict
) -> list[DictizedCronJob]:
    tk.check_access("ap_cron_get_job_list", context, data_dict)

    result = (
        CronJob.get_list(states=[data_dict["state"]])
        if data_dict.get("state")
        else CronJob.get_list()
    )

    return [job.dictize(context) for job in result]


@validate(cron_schema.update_cron_job)
def ap_cron_update_cron_job(
    context: types.Context, data_dict: types.DataDict
) -> DictizedCronJob:
    tk.check_access("ap_cron_update_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))

    for key, value in data_dict.items():
        setattr(job, key, value)

    job.updated_at = dt.utcnow()  # type: ignore

    model.Session.commit()

    log.info("[id:%s] Cron job has been updated: %s", job.id, data_dict)

    return job.dictize(context)


@validate(cron_schema.run_cron_job)
def ap_cron_run_cron_job(
    context: types.Context, data_dict: types.DataDict
) -> dict[str, Any]:
    tk.check_access("ap_cron_update_job", context, data_dict)

    job = cast(CronJob, CronJob.get(data_dict["id"]))

    if tk.h.ap_cron_is_job_running(job.dictize({})):
        log.exception("[id:%s] The cron job is already running.", job.id)
        raise tk.ValidationError({"message": tk._("The cron job is already running.")})

    job.last_run = dt.utcnow()  # type: ignore

    return {
        "job": job.dictize(context),
        "success": enqueue_cron_job(job),
    }
