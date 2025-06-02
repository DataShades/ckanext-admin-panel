from datetime import datetime as dt
from datetime import timezone

import click

import ckanext.ap_cron.utils as cron_utils
from ckanext.ap_cron.model import CronJob


@click.group()
def ap_cron():
    """Admin Panel Cron manage CLI commands"""
    pass


@ap_cron.command()
def trigger_jobs():
    """Enqueue the cron jobs that need to be run"""
    jobs_list = CronJob.get_list(
        states=[
            CronJob.State.failed,
            CronJob.State.finished,
            CronJob.State.active,
            CronJob.State.pending,
        ]
    )

    click.secho(f"Found {len(jobs_list)} active cron jobs.", fg="yellow")

    for job in jobs_list:
        if not _job_should_be_started(job):
            click.secho(f"Job {job} shouldn't be scheduled yet.", fg="green")
            continue

        click.secho(f"The job {job} has been added to the queue", fg="yellow")
        cron_utils.enqueue_cron_job(job)


def _job_should_be_started(job: CronJob) -> bool:
    """Check if it's time to run a job according to its schedule. If the `last_run`
    is None, it means that we never started this job and it's should be started."""
    if not job.last_run:
        return True

    now = dt.now(timezone.utc)
    next_run = cron_utils.get_next_run_datetime(job.last_run, job.schedule)  # type: ignore

    return next_run <= now


def get_commands():
    return [ap_cron]
