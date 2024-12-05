We utilize the `ISignal` interface for gathering configuration sections. For instance, to register a configuration section from your extension:

```python
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

The structure of the section config:

- `name` - defines the name of the configuration section
- `configs` - a list of configuration items

::: ap_main.types.SectionConfig
    options:
      show_source: true
      show_bases: false

The structure of the configuration item:

- `name` - defines the name of the configuration item link
- `blueprint` - indicates the configuration page blueprint
- `info` (optional, default: `No description`) - provides a description for the configuration link

::: ap_main.types.ConfigurationItem
    options:
      show_source: true
      show_bases: false

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

