from __future__ import annotations

import factory

from ckan.tests import factories

from ckanext.ap_support.model import Ticket, TicketMessage


class TicketFactory(factories.CKANFactory):
    """Factory for creating test tickets."""

    class Meta:
        model = Ticket
        action = "ap_support_ticket_create"

    subject = factory.Faker("sentence")
    text = factory.Faker("paragraph")
    category = "general"
    author_id = factory.LazyAttribute(lambda _: factories.User()["id"])


class TicketMessageFactory(factories.CKANFactory):
    """Factory for creating test ticket messages."""

    class Meta:
        model = TicketMessage
        action = "ap_support_message_create"

    ticket_id = factory.LazyAttribute(lambda _: TicketFactory()["id"])
    author_id = factory.LazyAttribute(lambda _: factories.User()["id"])
    content = factory.Faker("paragraph")
