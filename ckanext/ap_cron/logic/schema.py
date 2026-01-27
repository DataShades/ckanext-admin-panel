from ckan import types
from ckan.logic.schema import validator_args

from ckanext.ap_cron import config as cron_conf
from ckanext.ap_cron.model import CronJob

STATES = [
    CronJob.State.active,
    CronJob.State.disabled,
    CronJob.State.pending,
    CronJob.State.running,
    CronJob.State.failed,
    CronJob.State.finished,
]


@validator_args
def add_cron_job(  # noqa: PLR0913
    not_missing: types.Validator,
    default: types.ValidatorFactory,
    unicode_safe: types.Validator,
    convert_to_json_if_string: types.Validator,
    dict_only: types.Validator,
    cron_schedule_validator: types.Validator,
    int_validator: types.Validator,
    is_positive_integer: types.Validator,
    json_list_or_string: types.Validator,
    list_of_strings: types.Validator,
    cron_action_exists: types.Validator,
    one_of: types.ValidatorFactory,
) -> types.Schema:
    return {
        "name": [not_missing, unicode_safe],
        "schedule": [not_missing, unicode_safe, cron_schedule_validator],
        "actions": [
            not_missing,
            unicode_safe,
            json_list_or_string,
            list_of_strings,
            cron_action_exists,
        ],
        "timeout": [
            default(cron_conf.get_job_timeout()),
            int_validator,
            is_positive_integer,
        ],
        "data": [not_missing, convert_to_json_if_string, dict_only],
        "state": [default(CronJob.State.active), unicode_safe, one_of(STATES)],
    }


@validator_args
def get_cron_job(
    not_missing: types.Validator,
    unicode_safe: types.Validator,
    cron_job_exists: types.Validator,
) -> types.Schema:
    return {"id": [not_missing, unicode_safe, cron_job_exists]}


@validator_args
def remove_cron_job(
    not_missing: types.Validator,
    unicode_safe: types.Validator,
    cron_job_exists: types.Validator,
) -> types.Schema:
    return {"id": [not_missing, unicode_safe, cron_job_exists]}


@validator_args
def get_cron_job_list(
    ignore_missing: types.Validator,
    unicode_safe: types.Validator,
    one_of: types.ValidatorFactory,
) -> types.Schema:
    return {"state": [ignore_missing, unicode_safe, one_of(STATES)]}


@validator_args
def run_cron_job(
    not_missing: types.Validator,
    unicode_safe: types.Validator,
    cron_job_exists: types.Validator,
) -> types.Schema:
    return {"id": [not_missing, unicode_safe, cron_job_exists]}


@validator_args
def update_cron_job(  # noqa: PLR0913
    not_missing: types.Validator,
    ignore_missing: types.Validator,
    unicode_safe: types.Validator,
    convert_to_json_if_string: types.Validator,
    dict_only: types.Validator,
    int_validator: types.Validator,
    is_positive_integer: types.Validator,
    json_list_or_string: types.Validator,
    ignore: types.Validator,
    one_of: types.ValidatorFactory,
    isodate: types.Validator,
    cron_job_exists: types.Validator,
    cron_schedule_validator: types.Validator,
    cron_actions_to_string: types.Validator,
    cron_kwargs_provided: types.Validator,
) -> types.Schema:
    return {
        "id": [not_missing, unicode_safe, cron_job_exists],
        "name": [ignore_missing, unicode_safe],
        "schedule": [ignore_missing, unicode_safe, cron_schedule_validator],
        "last_run": [ignore_missing, isodate],
        "actions": [
            ignore_missing,
            unicode_safe,
            json_list_or_string,
            cron_actions_to_string,
        ],
        "timeout": [
            ignore_missing,
            int_validator,
            is_positive_integer,
        ],
        "data": [
            ignore_missing,
            convert_to_json_if_string,
            dict_only,
            cron_kwargs_provided,
        ],
        "state": [ignore_missing, unicode_safe, one_of(STATES)],
        "__extras": [ignore],
        "__junk": [ignore],
    }
