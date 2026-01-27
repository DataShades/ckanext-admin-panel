from __future__ import annotations

import ckan.model as model
import ckan.plugins.toolkit as tk
import pytest

import ckanext.ap_support.logic.validators as support_validators


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestTicketIdExists:
    """Test the ticket_id_exists validator."""

    def test_valid_ticket_id(self, ticket):
        """Test that a valid ticket ID passes validation."""
        result = support_validators.ticket_id_exists(
            ticket["id"], {"session": model.Session}
        )
        assert result == ticket["id"]

    def test_invalid_ticket_id(self):
        """Test that an invalid ticket ID raises an error."""
        with pytest.raises(tk.Invalid, match="Ticket not found"):
            support_validators.ticket_id_exists("999999", {"session": model.Session})

    def test_none_ticket_id(self):
        """Test that None ticket ID raises an error."""
        with pytest.raises(tk.Invalid, match="Ticket not found"):
            support_validators.ticket_id_exists(None, {"session": model.Session})


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestMessageIdExists:
    """Test the message_id_exists validator."""

    def test_valid_message_id(self, ticket, user):
        """Test that a valid message ID passes validation."""
        from ckan.tests.helpers import call_action

        # Create a message
        call_action(
            "ap_support_message_create",
            ticket_id=ticket["id"],
            author_id=user["id"],
            content="Test message",
        )

        # Get the message ID
        updated_ticket = call_action("ap_support_ticket_show", id=ticket["id"])
        message_id = updated_ticket["messages"][0]["id"]

        result = support_validators.message_id_exists(
            message_id, {"session": model.Session}
        )
        assert result == message_id

    def test_invalid_message_id(self):
        """Test that an invalid message ID raises an error."""
        with pytest.raises(tk.Invalid, match="Message not found"):
            support_validators.message_id_exists("999999", {"session": model.Session})

    def test_none_message_id(self):
        """Test that None message ID raises an error."""
        with pytest.raises(tk.Invalid, match="Message not found"):
            support_validators.message_id_exists(None, {"session": model.Session})


class TestCategoryValidator:
    """Test the ap_support_category_validator."""

    @pytest.mark.parametrize(
        "category",
        [
            "Feature request",
            "Data request",
            "Bug report",
            "Other",
        ],
    )
    def test_valid_categories(self, category):
        """Test that valid categories pass validation."""
        result = support_validators.ap_support_category_validator(category)
        assert result == category

    @pytest.mark.parametrize(
        "category",
        [
            "Invalid Category",
            "random",
            "test",
            "",
        ],
    )
    def test_invalid_categories(self, category):
        """Test that invalid categories raise an error."""
        with pytest.raises(tk.Invalid, match="is not allowed"):
            support_validators.ap_support_category_validator(category)

    def test_none_category(self):
        """Test that None category raises an error."""
        with pytest.raises(tk.Invalid, match="is not allowed"):
            support_validators.ap_support_category_validator(None)
