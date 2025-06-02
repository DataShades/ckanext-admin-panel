from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.types as types

from ckanext.ap_support.collection import SupportCollection
from ckanext.ap_support.formatters import get_formatters

from ckanext.ap_main.interfaces import IAdminPanel
from ckanext.ap_main.types import Formatter


@tk.blanket.blueprints
@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.validators
@tk.blanket.helpers
class AdminPanelSupportPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ISignal)
    p.implements(IAdminPanel, inherit=True)

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
            tk.signals.ckanext.signal("collection:register_collections"): [
                self.collect_collections_subs
            ],
        }

    @staticmethod
    def collect_collections_subs(sender: None):
        return {"ap-support": SupportCollection}

    @staticmethod
    def collect_config_sections_subs(sender: None):
        return {
            "name": "Support system",
            "configs": [
                {
                    "name": "Global settings",
                    "blueprint": "ap_user.list",
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

    def get_formatters(self) -> dict[str, Formatter]:
        return get_formatters()
