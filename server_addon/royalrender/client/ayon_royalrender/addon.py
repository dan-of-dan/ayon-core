# -*- coding: utf-8 -*-
"""Module providing support for Royal Render."""
import os

from ayon_core.addon import AYONAddon, IPluginPaths

from .version import __version__


class RoyalRenderAddon(AYONAddon, IPluginPaths):
    """Class providing basic Royal Render implementation logic."""
    name = "royalrender"
    version = __version__

    def initialize(self, studio_settings):
        # type: (dict) -> None
        rr_settings = studio_settings[self.name]
        self.enabled = rr_settings["enabled"]
        self.rr_paths = rr_settings.get("rr_paths")

    @staticmethod
    def get_plugin_paths():
        # type: () -> dict
        """Royal Render plugin paths.

        Returns:
            dict: Dictionary of plugin paths for RR.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return {
            "publish": [os.path.join(current_dir, "plugins", "publish")]
        }
