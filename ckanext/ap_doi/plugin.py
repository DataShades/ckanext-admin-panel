from __future__ import annotations

import logging
from os import path
from typing import Any

from yaml import safe_load

import ckan.logic as logic
import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.config.declaration import Declaration, Key
from ckan.types import SignalMapping

import ckanext.ap_doi.config as config
import ckanext.ap_doi.const as const
import ckanext.ap_doi.utils as utils
from ckanext.doi.plugin import DOIPlugin

import ckanext.ap_main.types as ap_types

log = logging.getLogger(__name__)


@tk.blanket.blueprints
@tk.blanket.actions
@tk.blanket.auth_functions
class AdminPanelDoiPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ISignal)
    p.implements(p.IConfigDeclaration)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "ap_doi")

    # IPackageController

    def after_dataset_show(self, context: Any, pkg_dict: dict[str, Any]):
        if not pkg_dict.get("author"):
            pkg_dict = utils.set_package_author(pkg_dict)

        return pkg_dict

    def after_dataset_update(self, context: Any, pkg_dict: dict[str, Any]):
        if not pkg_dict.get("author"):
            pkg_dict = utils.set_package_author(pkg_dict)

        doi_to_update = utils.get_doi_to_update(context["model"], pkg_dict["id"])
        flake_exists = utils.package_already_in_flake(
            const.DOI_FLAKE_NAME, pkg_dict["id"]
        )
        is_old_doi = doi_to_update.published is not None

        # We need to create flake only for old DOIs,
        # because if it is a newly generated,
        # it will be shown as a package without DOI,
        # and we don't have to check its metadata updates
        if not flake_exists and is_old_doi:
            utils.add_package_to_flake(const.DOI_FLAKE_NAME, pkg_dict["id"])

        return pkg_dict

    # ISignal

    def get_signal_subscriptions(self) -> SignalMapping:
        return {
            tk.signals.ckanext.signal("ap_main:collect_config_sections"): [
                self.collect_config_sections_subscriber,
            ],
            tk.signals.ckanext.signal("ap_main:collect_config_schemas"): [
                self.collect_config_schemas_subs
            ],
        }

    @staticmethod
    def collect_config_sections_subscriber(sender: None):
        return ap_types.SectionConfig(
            name="DOI",
            configs=[
                ap_types.ConfigurationItem(
                    name="Dashboard",
                    blueprint="doi_dashboard.list",
                ),
                ap_types.ConfigurationItem(
                    name="DOI settings",
                    blueprint="doi_dashboard.config",
                ),
            ],
        )

    @staticmethod
    def collect_config_schemas_subs(sender: None):
        return ["ckanext.ap_doi:config_schema.yaml"]

    # IConfigDeclaration

    def declare_config_options(self, declaration: Declaration, key: Key):
        logic.clear_validators_cache()

        with open(path.dirname(__file__) + "/config_declaration.yaml") as file:
            data_dict = safe_load(file)

        return declaration.load_dict(data_dict)


class ApDOIPlugin(DOIPlugin):
    def after_dataset_create(self, context, pkg_dict):
        if config.is_mock_api_calls():
            return

        try:
            super(ApDOIPlugin, self).after_dataset_create(context, pkg_dict)
        except Exception as e:
            log.error(e)

    ## IPackageController
    def after_dataset_update(self, context, pkg_dict):
        if config.is_mock_api_calls():
            return

        try:
            super(ApDOIPlugin, self).after_dataset_update(context, pkg_dict)
        except Exception as e:
            log.error(e)
