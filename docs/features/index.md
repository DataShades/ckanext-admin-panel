In addition to the main plugin, `ckanext-admin-panel` introduces several extensions that enhance the basic functionality by providing convenient tools for working with logs, cron jobs, and more.

The following plugins are available:

- [`admin_panel_log`](./logging/index.md): Provides a simple interface for viewing and filtering the logs.
- [`admin_panel_cron`](./cron/index.md): Allows you to manage cron jobs through the web interface.
- [`admin_panel_doi`](./doi/index.md): Adds a DOI support to the CKAN datasets.

The `admin_panel_support` plugin was removed in 3.0.0 — support ticketing now
lives in the standalone [`ckanext-issues`](https://github.com/DataShades/ckanext-issues)
extension. See [Support ticketing](./support.md) for the upgrade guide.
