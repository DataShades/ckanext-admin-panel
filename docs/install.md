# Installation

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | no          |
| 2.10         | yes         |
| 2.11         | yes         |

## Installation

1. Install the extension from `PyPI`:
    ```sh
    pip install ckanext-admin-panel
    ```

2. Enable the main plugin and extra plugins you want to use in your CKAN configuration file (e.g. `ckan.ini` or `production.ini`):

    ```ini
    ckan.plugins = ... admin_panel admin_panel_log ...
    ```

3. Initialize all missing tables with: `ckan db pending-migrations --apply`

## Developer installation

To install `ckanext-admin-panel` for development, activate your CKAN virtualenv and do:

    git clone https://github.com/DataShades/ckanext-admin-panel.git
    cd ckanext-admin-panel
    pip install -e .

## Extra plugins

In addition to the main plugin, `ckanext-admin-panel` introduces several extensions that enhance the basic functionality by providing convenient tools for working with logs, cron jobs, and more.

See the [Features](./features/index.md) section for a list of available plugins and information on how to enable them.

## Dependencies

The extension requires the following CKAN extensions to be installed and enabled:

1. [`ckanext-scheming`](https://github.com/ckan/ckanext-scheming):
We're using the scheming extension to create custom forms for plugin configuration pages. See the [documentation](./register_config_page.md) for more information.

2. [`ckanext-editable-config`](https://github.com/ckan/ckanext-editable-config):
The `ckanext-editable-config` extension allows you to edit the CKAN configuration in runtime.
