from __future__ import annotations

from typing import Any, Callable

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.lib.redis import connect_to_redis
from ckan.types import SignalMapping

import ckanext.ap_main.types as ap_types
from ckanext.ap_main import helpers, utils
from ckanext.ap_main.formatters import get_formatters
from ckanext.ap_main.interfaces import IAdminPanel


@tk.blanket.blueprints
@tk.blanket.auth_functions
class AdminPanelPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IConfigurable)
    p.implements(p.IBlueprint)
    p.implements(p.ISignal)
    p.implements(p.ITemplateHelpers)
    p.implements(IAdminPanel, inherit=True)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_resource("assets", "admin_panel")

    # IConfigurable

    def configure(self, config: tk.CKANConfig) -> None:
        # Remove toolbar cache
        with connect_to_redis() as conn:
            for key in conn.scan_iter("ckanext.ap_main.helpers:get_toolbar_structure*"):
                conn.delete(key)

    # ITemplateHelpers

    def get_helpers(self) -> dict[str, Callable[..., Any]]:
        return helpers.get_helpers()

    # IAdminPanel

    def get_formatters(self) -> dict[str, ap_types.Formatter]:
        return get_formatters()

    # ISignal

    def get_signal_subscriptions(self) -> SignalMapping:
        return {
            utils.collect_sections_signal: [
                self.collect_config_sections_subscriber,
            ],
        }

    @classmethod
    def collect_config_sections_subscriber(cls, sender: None):
        return ap_types.SectionConfig(
            name="Basic site settings",
            configs=[
                ap_types.ConfigurationItem(
                    name=tk._("CKAN configuration"),
                    info=tk._("CKAN site config options"),
                    blueprint=(
                        "ap_basic.editable_config"
                        if p.plugin_loaded("editable_config")
                        else "ap_basic.config"
                    ),
                ),
            ],
        )
