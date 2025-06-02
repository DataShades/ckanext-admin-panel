from __future__ import annotations

import datetime
import logging
from typing import Any

from croniter import croniter

import ckan.plugins.toolkit as tk

from ckanext.ap_cron.const import ERRORS, KWARGS, LOG_NAME, RESULTS
from ckanext.ap_cron.model import CronJob
from ckanext.ap_cron.types import DictizedCronJob

log = logging.getLogger(LOG_NAME)


def get_next_run_datetime(date: datetime.datetime, schedule: str) -> datetime.datetime:
    """Get a datetime object of the next job run"""
    return croniter(schedule, date).get_next(datetime.datetime)


def enqueue_cron_job(job: CronJob) -> bool:
    if not job:
        log.exception("[id:%s] Unable to find a cron job", job.id)
        return False

    # throw away old errors on a new run
    job.data.pop(ERRORS, None)

    _update_job_state({"id": job.id, "state": CronJob.State.pending, "data": job.data})

    log.info("[id:%s] The job %s has been added to the queue", job.id, job)

    try:
        tk.enqueue_job(
            cron_job_pipe,
            [
                {
                    "job_type": "ap_cron_job",
                    "data": {
                        "cron_job": job,
                        "actions": job.get_actions,
                        "kwargs": job.data.get(KWARGS, {}),
                    },
                }
            ],
            rq_kwargs={
                "timeout": job.timeout,
                "on_failure": job_failure_callback,
            },
        )
    except Exception:
        log.exception("[id:%s] Unable to enqueued cron job", job.id)
        return False

    log.info("[id:%s] Cron job has been enququed", job.id)

    return True


def job_failure_callback(rq_job, connection, type, value, traceback):
    """Mark a cron job as failed if the rq throw an exception"""
    job: CronJob = rq_job.args[0]["data"]["cron_job"]
    job.data[ERRORS] = str(value)

    _update_job_state({"id": job.id, "state": CronJob.State.running, "data": job.data})


def cron_job_pipe(data_dict: dict[str, Any]) -> DictizedCronJob:
    """This function runs a list of actions for a specific cron job successively.
    The result of the action is passed to the next one."""

    job: CronJob = data_dict["data"]["cron_job"]

    log.info("[id:%s] The cron job has been started", job.id)

    _update_job_state(
        {
            "id": job.id,
            "state": CronJob.State.running,
            "last_run": datetime.datetime.utcnow(),
        }
    )

    payload = data_dict["data"].get(KWARGS, {})

    for action in data_dict["data"]["actions"]:
        log.info("[id:%s] Starting to run an action %s", job.id, action)

        try:
            result = tk.get_action(action)({"ignore_auth": True}, payload)
            payload = result if result else {}
        except tk.ValidationError as e:
            e.error_dict["action_name"] = action
            e.error_dict[KWARGS] = payload  # type: ignore
            job.data[ERRORS] = e.error_dict

            log.exception(
                "[id:%s] An action %s has failed. Terminating...", job.id, action
            )
            log.exception("[id:%s] Error dict %s", job.id, e.error_dict)

            return _update_job_state(
                {"id": job.id, "state": CronJob.State.failed, "data": job.data}
            )
        else:
            job.data[RESULTS] = result

        log.info("[id:%s] The action %s was executed successfully...", job.id, action)

    log.info("[id:%s] The cron job has successfuly finished", job.id)

    return _update_job_state(
        {"id": job.id, "state": CronJob.State.finished, "data": job.data}
    )


def _update_job_state(data: dict[str, Any]) -> DictizedCronJob:
    return tk.get_action("ap_cron_update_cron_job")({"ignore_auth": True}, data)
