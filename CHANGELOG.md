# Changelog

All notable changes to this project will be documented in this file.

## [unreleased]

### 🚀 Features

- Replace user collection with custom table

## [1.2.0] - 2025-05-02

### 🚀 Features

- Restyle admin panel, part 1
- Restyle admin panel, part 2
- Restyle admin panel, part 3
- Replace collections with custom table and tabulator, wip

### 🐛 Bug Fixes

- Fix tom_select macro
- Fix ap-confirm-action.js, fix tom_select macro

### 💼 Other

- Set default delimiter for tom-select to ,
- Update tom_select form snippet and macro

## [1.1.19] - 2024-12-05

### 📚 Documentation

- Write a full documentation using mkdocs

## [1.1.18] - 2024-11-12

### 🚀 Features

- Sort registered toolbar config options by name
- Rework user_link renderer to use avatar placeholder
- Add tom_tags.html form snippet
- Change the ap-tom-select default delimiter

### 🐛 Bug Fixes

- Fix tom-select inputs height

## [1.1.16] - 2024-10-24

### 🚀 Features

- Add dark/light theme switcher, polish styles
- Add a basic interface to register config sections
- Configuration page for ckanext-editable-config
- Working on user list page
- Working on user list page part2
- Add a user creation page for a sysadmin
- Add a basic implementation of logs page
- Create a  snippet
- Add multi_select macro
- Implement filter, search, sort for logs page
- Implement clearing logs
- Rewrite db handler init, change engine for ApLogs table
- Implement logs disabled page
- Allow updating toolbar from plugins
- Allow disabling search and theme switcher
- Add Role field to User add form
- Add ap-bulk-check script
- Basic implementation of content page, WIP
- Basic implementation of content page, WIP part 2
- Add temporary link to old admin in toolbar
- Basic implementation of content page, FINISH
- Add an ability to provide a function for rendering column
- Add ckan account header buttons to our toolbar
- Add a unique css class for each page
- Add mock for cron jobs page
- Implement editing of a cron job
- Implement row display feature to have more control
- Add a cli command to trigger cron
- Implement bulk actions
- Implement run active jobs button
- Add IAPCron interface, add method to exclude actions
- Use exclude_action method in cron_action_exists validator
- Create an extension, add model, migration, other boilerplate code
- Add modal to create ticket and actions, schemas and validator
- Basic implementation of list page and mock for read page
- Add ckanext-collection
- Add arbitrary schema support polyfill
- Add configuration page generic view
- Add ap-disable-field script
- Add ap_example plugin for dev purposes
- Add GlobalAction filter for collections
- Use signals for collecting config pages
- Ap_doi plugin

### 🐛 Bug Fixes

- Fix accordion collapsing
- Fix dark them flickering, fix dropdown on mobile
- Fix applying color schema script in templates
- Interfaces.py typing
- Use h.url_for
- User list, user add pages
- Allow multi params for ap_add_url_param
- Format log message to trigger lazy interpolation
- Fix toolbar scripts
- Catch errors on content bulk action
- Extend js module properly, to avoid changing core one
- Fix regression after plugin separation
- Fix table sort and ordering feature
- Fix navbar nav-item styles
- Fix css z-index for an admin panel when in facets on mobile
- Fix regression after cron migration to collection
- Fix ApConfigurationPageView generic redirect after post
- Restore config reset
- Fix toolbar user avar size
- Move tooltip reinit into ap-tooltip module
- Update cron manager pipe logic
- Add init to logic folder
- Fix bulk user state change
- Add editable config to requirements
- Fix files and editable config required versions
- Fix admin panel visual issues
- Catch doi errors, cause ckanext-doi is too problematic...
- Fix ap_doi user_show context

### 💼 Other

- Style modals, add and style breadcrumbs
- People list
- Table filter css
- Extend confirm-action.js to send submit button with form
- Drop partial log clear for now
- Add some blocks for toolbar.html to extend easier
- Disable theme change script if switcher is disabled
- Add active class on current top level page
- Use CKAN brand image for logo
- Scale logo
- Fix table styles
- Update a cron manage buttons
- Pin last_run properly, sort by last_run by default, make column sortable
- Update generate_page_unique_class logic
- Improve json renderer
- Update example, add summetnote wysywig
- Update logs to use global-action ButtonFilter
- Remove unused code, move renderers, add ap-copy-to-clipboard script, add badge styles
- Add ap-bulk-check reinit after htmx request
- Clear validators cache to allow custom validators for cd
- Remove unused signal
- Move to collection, add ckeditor support
- Update modal response styles
- Remove search bar as it's not used
- Extract logs into a separate module
- Do not render empty toolbar item
- Fix fake doi published date
- Multiple fixes for cron manager, other fixes
- Add trim_string renderer
- Save cron job result
- Add after and before config update interface methods
- Add tom_select macro, form_snippet and js wrapper

### 🚜 Refactor

- Remove trash bin page
- Rework ap_table_column
- Move renderers to interface
- Disable not implemented toolbar and config options for now
- Move logs and users to collections
- Clear button refresh collection in-place
- Fix collection types
- Replace default value serializers with col renderers
- Use signals to register config schemas

### 📚 Documentation

- Add docstrings for helpers, add attributes support for ap_action
- Update doc, add todo
- Update todo
- Update readme
- Update readme
- Add doc about registering config options
- Add doc about registering config options, part 2
- Add doc about registering config options, part 3
- Add doc about registering config options, part 4
- Add doc about registering config options, part 5
- Write cron manager doc
- Write cron manager doc, part 2
- Write cron manager doc, part 3

### 🎨 Styling

- Fix table layout
- Update table layout

### ⚙️ Miscellaneous Tasks

- Remove shadowed implementations of TemplateHelpers and AuthFunctions
- Add makefile and git-changelog to requirements
- Fix tests
- Set minimal python version to 3.8
- Switch to blueprints blanket
- Add styles for multiline admin-toolbar
- Set pyright python to v3.8
- Update readme
- Update test GH workflow
- Use <p/> for config description in editable config
- Document collection helpers
- Add reset button to autogenerated config form; transform current config values to strings
- Remove unused code after migration to collections
- Bump collections
- Remove file dependency
- Py3.12 compatibility

<!-- generated by git-cliff -->
