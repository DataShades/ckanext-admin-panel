from __future__ import annotations

import ckan.plugins.toolkit as tk

# Fired after a new ticket is persisted.
# sender  : None
# kwargs  : ticket (DictizedTicket)
ticket_created = tk.signals.ckanext.signal(
    "ap_support:ticket_created",
    "Fired when a new support ticket is created",
)

# Fired after a new message is persisted on an existing ticket.
# sender  : None
# kwargs  : ticket (DictizedTicket), message (DictizedMessage)
message_created = tk.signals.ckanext.signal(
    "ap_support:message_created",
    "Fired when a new message is added to a support ticket",
)


# Fired after a ticket is updated (status, assignee, etc.)
# sender  : None
# kwargs  : ticket (DictizedTicket)
ticket_updated = tk.signals.ckanext.signal(
    "ap_support:ticket_updated",
    "Fired when a support ticket is updated",
)
