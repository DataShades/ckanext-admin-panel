# Support ticketing (moved to `ckanext-issues`)

!!! warning "Removed in 3.0.0"
    The `admin_panel_support` plugin that used to ship with
    `ckanext-admin-panel` has been extracted into a separate, self-contained
    extension: [`ckanext-issues`](https://github.com/DataShades/ckanext-issues).

## Upgrade steps

1. Install the new extension:

    ```sh
    pip install ckanext-issues
    ```

2. Update `ckan.plugins` in your CKAN config — replace `admin_panel_support`
   with `issues`, and make sure `tables` is listed before it:

    ```ini
    ckan.plugins = ... tables issues
    ```

3. Create the new tables:

    ```sh
    ckan db upgrade -p issues
    ```

4. Rename config options:

    | Old | New |
    | --- | --- |
    | `ckanext.admin_panel.support.category_list` | `ckanext.issues.category_list` |
    | `ckanext.admin_panel.support.notify_on_new_ticket` | `ckanext.issues.notify_on_new_ticket` |
    | `ckanext.admin_panel.support.notify_on_new_message` | `ckanext.issues.notify_on_new_message` |
    | `ckanext.admin_panel.support.notify_on_ticket_update` | `ckanext.issues.notify_on_ticket_update` |

5. If you overrode any `ap_support/*` templates, move them to `issues/*`. The
   URL prefix also changed: `/admin-panel/support` → `/issues` (and the
   sysadmin dashboard is at `/issues/admin`).

## Migrating existing ticket data

The extraction only renamed the tables (`ap_support_ticket` →
`issues_ticket`, `ap_support_ticket_message` → `issues_ticket_message`); the
columns are identical. After running `ckan db upgrade -p issues`, copy the
rows over:

```sql
INSERT INTO issues_ticket
    SELECT * FROM ap_support_ticket;

INSERT INTO issues_ticket_message
    SELECT * FROM ap_support_ticket_message;

-- keep the id sequences ahead of the imported rows
SELECT setval('issues_ticket_id_seq',
              (SELECT max(id) FROM issues_ticket));
SELECT setval('issues_ticket_message_id_seq',
              (SELECT max(id) FROM issues_ticket_message));
```

Once you have verified the data in the new UI, drop the old objects:

```sql
DROP TABLE ap_support_ticket_message;
DROP TABLE ap_support_ticket;
DROP TABLE admin_panel_support_alembic_version;
```
