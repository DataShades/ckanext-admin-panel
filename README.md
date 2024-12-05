
[![Tests](https://github.com/DataShades/ckanext-admin-panel/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-admin-panel/actions)

# ckanext-admin-panel

Next generation admin interface for CKAN. See the [extended documentation](https://datashades.github.io/ckanext-admin-panel/) for more information.

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

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
