from __future__ import annotations

from typing import Any, Callable

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.ap_cron import helpers
from ckanext.ap_cron.cli import get_commands
from ckanext.ap_cron.col_renderers import get_renderers
from ckanext.ap_cron.collection import CronCollection
from ckanext.collection.interfaces import CollectionFactory, ICollection

import ckanext.ap_main.types as ap_types
from ckanext.ap_main.interfaces import IAdminPanel
from ckanext.ap_main.types import ColRenderer


@tk.blanket.blueprints
@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.validators
class AdminPanelCronPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    # p.implements(p.IConfigurable)
    p.implements(p.IBlueprint)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IClick)
    p.implements(IAdminPanel, inherit=True)
    p.implements(ICollection, inherit=True)

    # IConfigurer

    def update_config(self, config_: tk.CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "ap_cron")

    # IConfigurable

    # def configure(self, config: tk.CKANConfig) -> None:
    #     from ckanext.ap_cron.utils import enqueue_cron_job

    #     jobs_list = cron_model.CronJob.get_list(states=[cron_model.CronJob.State.new])

    #     for job in jobs_list:
    #         if job.schedule != CronSchedule.reboot.value:
    #             continue

    #         enqueue_cron_job(job)

    # ITemplateHelpers

    def get_helpers(self) -> dict[str, Callable[..., Any]]:
        return helpers.get_helpers()

    # IAdminPanel

    def register_toolbar_button(
        self, toolbar_buttons_list: list[ap_types.ToolbarButton]
    ) -> list[ap_types.ToolbarButton]:
        """Extension will receive the list of toolbar button objects."""

        for button in toolbar_buttons_list:
            if button.get("label") == "Reports":
                button.setdefault("subitems", [])

                button["subitems"].append(  # type: ignore
                    ap_types.ToolbarButton(
                        label=tk._("Cron jobs"),
                        url=tk.url_for("ap_cron.manage"),
                    )
                )

        return toolbar_buttons_list

    def get_col_renderers(self) -> dict[str, ColRenderer]:
        return get_renderers()

    # IClick

    def get_commands(self) -> list[Any]:
        return get_commands()

    # ICollection

    def get_collection_factories(self) -> dict[str, CollectionFactory]:
        return {"ap-cron": CronCollection}
