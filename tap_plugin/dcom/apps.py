"""TAP dcom plugin AppConfig.

`name` is derived from the module path; `label` and `verbose_name` come from the
manifest. dcom registers no collectors and no panel types, so `ready()` is the
base class's.
"""

from tap_plugins.base import TapPluginConfig


class DcomConfig(TapPluginConfig):
    pass
