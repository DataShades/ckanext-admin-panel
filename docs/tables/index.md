# Tables

To represent the tabular data in the admin panel, we use [tabulator.js](https://tabulator.info/).

To create a table, you have to inherit the `TableDefinition` class and implement the `get_raw_data` method.

## Simple Approach

Here's a simple example of creating a table:

```python
from ckanext.ap_main.table import TableDefinition

class MyTable(TableDefinition):
    def get_raw_data(self):
        return [
            {
                "id": "1",
                "title": "Welcome to CKAN",
                "author": "admin",
                "created": "2024-01-15",
                "status": "published"
            },
            {
                "id": "2",
                "title": "Getting Started Guide",
                "author": "editor",
                "created": "2024-01-16",
                "status": "draft"
            }
        ]

    def get_columns(self):
        return [
            {"field": "id", "title": "ID", "width": 60},
            {"field": "title", "title": "Title", "minWidth": 200},
            {"field": "author", "title": "Author"},
            {"field": "created", "title": "Created"},
            {"field": "status", "title": "Status"}
        ]
```

## Advanced Approach

For more complex tables with formatters, actions, and global actions, you can use the advanced approach:

```python
from ckanext.ap_main.table import TableDefinition, ColumnDefinition, ActionDefinition, GlobalActionDefinition

class UserTable(TableDefinition):
    def __init__(self):
        super().__init__(
            name="user",
            ajax_url=tk.url_for("ap_user.list", data=True),
            placeholder=tk._("No users found"),
            columns=[
                ColumnDefinition("id", visible=False, filterable=False),
                ColumnDefinition(
                    "name",
                    formatters=[("user_link", {})],
                    tabulator_formatter="html",
                    min_width=300,
                ),
                ColumnDefinition(
                    "fullname",
                    formatters=[("none_as_empty", {})],
                    min_width=200,
                ),
                ColumnDefinition(
                    "email",
                    formatters=[("none_as_empty", {})],
                    min_width=200,
                ),
                ColumnDefinition("state"),
                ColumnDefinition("sysadmin", formatters=[("bool", {})]),
                ColumnDefinition(
                    "actions",
                    formatters=[("actions", {})],
                    filterable=False,
                    tabulator_formatter="html",
                    sorter=None,
                    resizable=False,
                ),
            ],
            actions=[
                ActionDefinition(
                    "edit",
                    icon="fa fa-pencil",
                    endpoint="user.edit",
                    url_params={"id": "$id"},
                ),
                ActionDefinition(
                    "view",
                    icon="fa fa-eye",
                    endpoint="user.read",
                    url_params={"id": "$id"},
                ),
            ],
            global_actions=[
                GlobalActionDefinition(
                    action="add_sysadmin",
                    label="Add sysadmin role to selected users"
                ),
                GlobalActionDefinition(
                    action="remove_sysadmin",
                    label="Remove sysadmin role from selected users",
                ),
                GlobalActionDefinition(
                    action="block",
                    label="Block selected users"
                ),
                GlobalActionDefinition(
                    action="unblock",
                    label="Unblock selected users"
                ),
            ],
        )

    def get_raw_data(self):
        query = (
            model.Session.query(
                model.User.id.label("id"),
                model.User.name.label("name"),
                model.User.fullname.label("fullname"),
                model.User.email.label("email"),
                model.User.state.label("state"),
                model.User.sysadmin.label("sysadmin"),
            )
            .filter(model.User.name != tk.config["ckan.site_id"])
            .order_by(model.User.name)
        )

        columns = ["id", "name", "fullname", "email", "state", "sysadmin"]
        return [dict(zip(columns, row)) for row in query.all()]
```

The `get_raw_data` method should return a list of dictionaries, where the keys are the column names and the values are the column values.

### Column Definition

The `ColumnDefinition` class allows you to define how each column should be rendered:

::: ap_main.table.ColumnDefinition


### Actions

You can define two types of actions:

1. Row Actions: Actions that can be performed on individual rows
2. Global Actions: Actions that can be performed on multiple selected rows

Actions are defined using `ActionDefinition` and `GlobalActionDefinition` classes respectively.
