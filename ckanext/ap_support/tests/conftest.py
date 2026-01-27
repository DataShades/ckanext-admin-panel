import pytest
from pytest_factoryboy import register

import ckanext.ap_support.tests.factories as factories

register(factories.TicketFactory, "ticket")
register(factories.TicketMessageFactory, "ticket_message")


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("ap_support")
