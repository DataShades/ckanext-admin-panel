import pytest
from faker import Faker
from pytest_factoryboy import register

import ckanext.ap_cron.tests.factories as local_factories

fake = Faker()

register(local_factories.CronJobFactory, "cron_job")


@pytest.fixture()
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("admin_panel_cron")
