
[![Tests](https://github.com/DataShades/ckanext-admin-panel/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-admin-panel/actions)

# ckanext-admin-panel

Next generation admin interface for CKAN.

## Content

- [ckanext-admin-panel](#ckanext-admin-panel)
  - [Content](#content)
  - [TODO](#todo)
  - [Registering config sections](#registering-config-sections)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Config settings](#config-settings)
  - [Enabling logging](#enabling-logging)
  - [Enable CRON logging](#enable-cron-logging)
  - [User CRON manager](#user-cron-manager)
    - [Scheduling](#scheduling)
    - [Create cron job](#create-cron-job)
  - [Developer installation](#developer-installation)
  - [Tests](#tests)
  - [License](#license)

## TODO
This extension is under development, so there are many things to do:

- CKAN forms:
	 - What do we want to do, if we are editing an entity from admin panel? Use default form or replace it with an admin version?
- Users:
	 - Add `User edit` page
- Recent log messages:
	 - We have  some types, that we don't want to include in list. E.g xloader resources. Research what is better to do with them.
	 - Rework the pagination approach, because the current naive one will work very slow on big amount of data
- Rewrite `user_list` action. Currently it's just a copy of contrib one with one small change. Maybe it's a good idea to write
  our own versatile version.
- Think about configuration section pages. Do we need a separate page for a section?
- Work on `Extensions` page. What do we want: replace `status_show`. This page should be more informative. Show here what extensions we are using with the respective versions. For now we don't have a standartized mechanism to retrieve versions from extensions, think about it.
- Work on `Available updates?` page. Show user if he could upgrade an extension or CKAN to a new version.
- Work on `Appearance` page. TODO
- Work on `Help` page. TODO


## Registering config sections

We utilize the `ISignal` interface for gathering configuration sections. For instance, to register a configuration section from your extension:

```py
from __future__ import annotations

import ckan.types as types
import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.ap_main.types as ap_types


class ExamplePlugin(p.SingletonPlugin):
    ...
    p.implements(p.ISignal)

    ...

    # ISignal

    def get_signal_subscriptions(self) -> types.SignalMapping:
        return {
            tk.signals.ckanext.signal("ap_main:collect_config_sections"): [
                self.collect_config_sections_subs
            ],
        }

    @staticmethod
    def collect_config_sections_subs(sender: None):
        return ap_types.SectionConfig(
            name="Example plugin configuration",
            configs=[
                ap_types.ConfigurationItem(
                    name="Configuration",
                    blueprint="example_plugin.config,
                    info="Basic configuration options",
                ),
            ],
        )
```

The structure of the section is outlined in the `SectionConfig` and `ConfigurationItem` [here](ckanext/ap_main/types.py).
You can import these structures and use them to assemble the section or just return a dictionary mirroring the same structure. This method works the same as described above:

```py
@staticmethod
def collect_config_sections_subs(sender: None):
    return {
        "name": "Example plugin configuration",
        "configs": [
            {
                "name": "Configuration",
                "blueprint": "example_plugin.config",
                "info": "Basic configuration options",
            },
        ],
    }
```

If the section with the specified `name` has already been registered by another plugin, the configuration options will be included into it.

The structure of `ConfigurationItem` is as follows:
- `name` - defines the name of the configuration section link
- `blueprint` - indicates the configuration page blueprint
- `info` (optional, default: `No description`) - provides a description for the configuration link


## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | no          |
| 2.10         | yes         |
| 2.11         | yes         |



## Installation

To install ckanext-admin-panel:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com/DataShades/ckanext-admin-panel.git
    cd ckanext-admin-panel
    pip install -e .
	pip install -r requirements.txt

3. Add `admin_panel admin_panel_cron` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

None at present

## Enabling logging
To store log messages in a database, you must enable the `admin_panel_log` extension, initialize the database log table,
and create a handler in your 'ckan.ini' file.

 1. Add `admin_panel_log` to the `ckan.plugins` setting in your CKAN config file.
 2. Initialize all missing tables with: `ckan db pending-migrations --apply`
 3. To register a handler, you must specify it in your CKAN configuration file. Due to some CKAN specifics, the logger needs to know the database URI to initialize itself. Provide it with the `kwargs` option.
	```
    [handler_dbHandler]
    class = ckanext.ap_log.log_handlers.DatabaseHandler
    formatter = generic
    level = NOTSET
    kwargs={"db_uri": "postgresql://ckan_default:pass@localhost/master"}
    ```

 4. The logging handler must be also included in `[handlers]` section.
	```
    [handlers]
    keys = console, dbHandler
	```
 5. The last thing you need to do is to add our handler to a logger you need. For example, if you want to log only `ckan` logs, do this:
	```
    [logger_ckan]
	level = INFO
	handlers = console, dbHandler
	```

## Enable CRON logging
Register a separate logger for a cron job logging. The DB handler must be initiated first if you want to have an access to logs via UI. Otherwise, you will be able to see logs only in CKAN logs files.

 1. Define a logger
	```
    [logger_ap_cron]
	level = DEBUG
	handlers = console, dbHandler
	qualname = ap_cron
	propagate = 0
	```
2. Use the newly created logger by specifiyng it in `loggers` section.
	```
    [loggers]
	keys = root, ckan, ckanext, werkzeug, flask_app, ap_cron
	```

## User CRON manager

### Scheduling
Each cron job can be manually triggered from the cron manager page. However, it's essential to schedule a single command with crontab to automatically trigger all jobs created within CKAN. For example:

    */10 * * * * /usr/lib/ckan/default/bin/ckan -c /etc/ckan/default/production.ini ap-cron trigger-jobs

This command checks all the jobs every 10 minutes to determine if they should be run again. Without scheduling this command, you can manually initiate a specific job through the user interface by clicking the `Run` button. Alternatively, you can execute all scheduled jobs by clicking the `Run active jobs` button.

### Create cron job
To create a cron job, navigate to the cron manager page and click the `Add cron job` button. 

Each job must include the following components:

- Name: A label used primarily in the UI for identification.
- Actions: One or more CKAN actions that will be executed.
- Data: JSON-formatted data that provides arguments to the initial action.
- Job Timeout: The maximum duration allowed for a job to run before it is deemed to have failed.
- Schedule: A cron expression that specifies the frequency and timing of the job execution.

It is important to note that console commands are not permitted within cron jobs for security reasons. Instead, only CKAN actions can be executed. You can chain multiple actions together; each subsequent action will receive the result of the previous one as its arguments.

## Developer installation

To install ckanext-admin-panel for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/DataShades/ckanext-admin-panel.git
    cd ckanext-admin-panel
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
