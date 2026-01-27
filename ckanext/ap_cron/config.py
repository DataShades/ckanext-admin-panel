import ckan.plugins.toolkit as tk

CONF_JOB_TIMEOUT = "ckanext.admin_panel.cron.job_timeout"
DEF_JOB_TIMEOUT = 3600


def get_job_timeout() -> int:
    """Get a cron job timeout."""
    return tk.asint(tk.config.get(CONF_JOB_TIMEOUT, DEF_JOB_TIMEOUT))
