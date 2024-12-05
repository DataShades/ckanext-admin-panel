To store log messages in a database, you must enable the `admin_panel_log` extension, initialize the database log table,
and create a handler in your ckan config file.

 1. Add `admin_panel_log` to the `ckan.plugins` setting in your CKAN config file.
 2. Initialize all missing tables with: `ckan db pending-migrations --apply`
 3. To register a handler, you must specify it in your CKAN configuration file. Due to some CKAN specifics, the logger needs to know the database URI to initialize itself. Provide it with the `kwargs` option.
	```ini
    [handler_dbHandler]
    class = ckanext.ap_log.log_handlers.DatabaseHandler
    formatter = generic
    level = NOTSET
    kwargs={"db_uri": "postgresql://ckan_default:pass@localhost/master"}
    ```

 4. The logging handler must be also included in `[handlers]` section.
	```ini
    [handlers]
    keys = console, dbHandler
	```
 5. The last thing you need to do is to add our handler to a logger you need. For example, if you want to log only `ckan` logs, do this:
	```ini
    [logger_ckan]
	level = INFO
	handlers = console, dbHandler
	```
