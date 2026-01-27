from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.tests import factories
from ckan.tests.helpers import call_auth


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestTicketAuth:
    """Test authorization for ticket operations."""

    def test_ticket_create_anon(self):
        """Test that anonymous users can create tickets."""
        # Anyone can create tickets
        result = call_auth(
            "ap_support_ticket_create", context={"user": None, "model": model}
        )
        assert result is True

    def test_ticket_create_regular_user(self, user):
        """Test that regular users can create tickets."""
        result = call_auth(
            "ap_support_ticket_create", context={"user": user["name"], "model": model}
        )
        assert result is True

    def test_ticket_delete_anon(self):
        """Test that anonymous users cannot delete tickets."""
        with pytest.raises(tk.NotAuthorized):
            call_auth(
                "ap_support_ticket_delete", context={"user": None, "model": model}
            )

    def test_ticket_delete_regular_user(self, user):
        """Test that regular users cannot delete tickets."""
        with pytest.raises(tk.NotAuthorized):
            call_auth(
                "ap_support_ticket_delete",
                context={"user": user["name"], "model": model},
            )

    def test_ticket_delete_sysadmin(self, sysadmin):
        """Test that sysadmins can delete tickets."""
        result = call_auth(
            "ap_support_ticket_delete",
            context={"user": sysadmin["name"], "model": model},
        )
        assert result is True


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestMessageAuth:
    """Test authorization for message operations."""

    def test_message_delete_anon(self):
        """Test that anonymous users cannot delete messages."""
        result = call_auth(
            "ap_support_message_delete",
            context={"user": None, "model": model},
            data_dict={"id": "1"},
        )
        assert result is False

    def test_message_delete_own_message(self, ticket, user):
        """Test that users can delete their own messages."""
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

        # Check auth for deleting own message
        user_obj = model.User.get(user["id"])
        result = call_auth(
            "ap_support_message_delete",
            context={"user": user["name"], "model": model, "auth_user_obj": user_obj},
            data_dict={"id": message_id},
        )
        assert result is True

    def test_message_delete_others_message(self, ticket, user):
        """Test that users cannot delete others' messages."""
        from ckan.tests.helpers import call_action

        # Create a message with a different user
        other_user = factories.User()
        call_action(
            "ap_support_message_create",
            ticket_id=ticket["id"],
            author_id=other_user["id"],
            content="Test message",
        )

        # Get the message ID
        updated_ticket = call_action("ap_support_ticket_show", id=ticket["id"])
        message_id = updated_ticket["messages"][0]["id"]

        # Check auth for deleting others' message
        user_obj = model.User.get(user["id"])
        result = call_auth(
            "ap_support_message_delete",
            context={"user": user["name"], "model": model, "auth_user_obj": user_obj},
            data_dict={"id": message_id},
        )
        assert result is False

    def test_message_delete_sysadmin(self, ticket, user, sysadmin):
        """Test that sysadmins can delete any message."""
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

        # Check auth for sysadmin
        result = call_auth(
            "ap_support_message_delete",
            context={"user": sysadmin["name"], "model": model},
            data_dict={"id": message_id},
        )
        assert result is True

    def test_message_update_anon(self):
        """Test that anonymous users cannot update messages."""
        result = call_auth(
            "ap_support_message_update",
            context={"user": None, "model": model},
            data_dict={"id": "1"},
        )
        assert result is False

    def test_message_update_own_message(self, ticket, user):
        """Test that users can update their own messages."""
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

        # Check auth for updating own message
        user_obj = model.User.get(user["id"])
        result = call_auth(
            "ap_support_message_update",
            context={"user": user["name"], "model": model, "auth_user_obj": user_obj},
            data_dict={"id": message_id},
        )
        assert result is True

    def test_message_update_others_message(self, ticket, user):
        """Test that users cannot update others' messages."""
        from ckan.tests.helpers import call_action

        # Create a message with a different user
        other_user = factories.User()
        call_action(
            "ap_support_message_create",
            ticket_id=ticket["id"],
            author_id=other_user["id"],
            content="Test message",
        )

        # Get the message ID
        updated_ticket = call_action("ap_support_ticket_show", id=ticket["id"])
        message_id = updated_ticket["messages"][0]["id"]

        # Check auth for updating others' message
        user_obj = model.User.get(user["id"])
        result = call_auth(
            "ap_support_message_update",
            context={"user": user["name"], "model": model, "auth_user_obj": user_obj},
            data_dict={"id": message_id},
        )
        assert result is False

    def test_message_update_sysadmin(self, ticket, user, sysadmin):
        """Test that sysadmins can update any message."""
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

        # Check auth for sysadmin
        result = call_auth(
            "ap_support_message_update",
            context={"user": sysadmin["name"], "model": model},
            data_dict={"id": message_id},
        )
        assert result is True
