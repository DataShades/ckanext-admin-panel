To enable the `admin_panel_cron` plugin, you need to add it to the `ckan.plugins` setting in your CKAN config file.

```ini
ckan.plugins = admin_panel admin_panel_cron
```

After that, initialize all missing tables with:
```bash
ckan db pending-migrations --apply
```

## Enable CRON logging
You can register a separate logger for a cron job logging. The DB handler must be initiated first if you want to have an access to logs via UI. Otherwise, you will be able to see logs only in CKAN logs files. See the [logging](../logging/index.md) section for more information.

Having a separate logger for cron jobs allows you to filter logs by the cron job name and to have a separate log file for them.

 1. Define a logger
    ```ini
    [logger_ap_cron]
    level = DEBUG
    handlers = console, dbHandler
    qualname = ap_cron
    propagate = 0
    ```
2. Use the newly created logger by specifiyng it in `loggers` section.
    ```ini
    [loggers]
    keys = root, ckan, ckanext, werkzeug, flask_app, ap_cron
    ```
