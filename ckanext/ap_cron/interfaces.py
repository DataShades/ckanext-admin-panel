from __future__ import annotations

from ckan import types
from ckan.plugins.interfaces import Interface


class IAPCron(Interface):
    def exclude_action(
        self, action_list: dict[str, types.Action]
    ) -> dict[str, types.Action]:
        """Exclude action from being used by cron job.

        By default, all the CKAN actions could be used by cron job. This method
        provides a possibiltiy to make an actions non-usable."""
        return action_list
