from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import types

from ckanext.ap_support import mailer
from ckanext.ap_support import signals as support_signals


@tk.blanket.blueprints
@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.validators
@tk.blanket.helpers
class AdminPanelSupportPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ISignal)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "ap_support")

    # ISignal

    def get_signal_subscriptions(self) -> types.SignalMapping:
        return {
            tk.signals.ckanext.signal("ap_main:collect_config_sections"): [
                self.collect_config_sections_subs
            ],
            support_signals.ticket_created: [
                mailer.notify_admins_on_new_ticket,
            ],
            support_signals.message_created: [
                mailer.notify_author_on_new_message,
            ],
            support_signals.ticket_updated: [
                mailer.notify_author_on_ticket_update,
            ],
        }

    @staticmethod
    def collect_config_sections_subs(sender: None):
        return {
            "name": "Support system",
            "configs": [
                {
                    "name": "Global settings",
                    "blueprint": "ap_support.list",  # TODO: add blueprint
                    "info": "Support system configuration",
                },
                {
                    "name": "Dashboard",
                    "blueprint": "ap_support.list",
                    "info": "Support dashboard",
                },
            ],
        }

    # IAdminPanel
