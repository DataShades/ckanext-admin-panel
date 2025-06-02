1. Enable the `doi` and `admin_panel_doi` extension in the CKAN configuration file (e.g. `production.ini`):

    ```ini
    ckan.plugins = ... ap_doi admin_panel_doi
    ```

2. Create the DOI database table:

    ```shell
    ckan -c production.ini doi initdb
    ```

## Dependencies

The DOI feature requires the following dependencies to be installed and enabled:

- `ckanext-admin-panel` plugin
- [`ckanext-doi`](https://github.com/NaturalHistoryMuseum/ckanext-doi) plugin
- [`ckanext-flakes`](https://github.com/DataShades/ckanext-flakes) plugin

Ensure, that you've installed the `ckanext-admin-panel` with the `doi` depdendencies, like this:
`pip install -e '.[doi]'`
