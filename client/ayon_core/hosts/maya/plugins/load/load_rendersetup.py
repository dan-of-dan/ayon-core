# -*- coding: utf-8 -*-
"""Load and update RenderSetup settings.

Working with RenderSetup setting is Maya is done utilizing json files.
When this json is loaded, it will overwrite all settings on RenderSetup
instance.
"""

import json
import sys
import six

from ayon_core.pipeline import (
    load,
    get_representation_path
)
from ayon_core.hosts.maya.api import lib
from ayon_core.hosts.maya.api.pipeline import containerise

from maya import cmds
import maya.app.renderSetup.model.renderSetup as renderSetup


class RenderSetupLoader(load.LoaderPlugin):
    """Load json preset for RenderSetup overwriting current one."""

    families = ["rendersetup"]
    representations = ["json"]
    defaults = ['Main']

    label = "Load RenderSetup template"
    icon = "tablet"
    color = "orange"

    def load(self, context, name, namespace, data):
        """Load RenderSetup settings."""

        # from ayon_core.hosts.maya.api.lib import namespaced

        folder_name = context["folder"]["name"]
        namespace = namespace or lib.unique_namespace(
            folder_name + "_",
            prefix="_" if folder_name[0].isdigit() else "",
            suffix="_",
        )
        path = self.filepath_from_context(context)
        self.log.info(">>> loading json [ {} ]".format(path))
        with open(path, "r") as file:
            renderSetup.instance().decode(
                json.load(file), renderSetup.DECODE_AND_OVERWRITE, None)

        nodes = []
        null = cmds.sets(name="null_SET", empty=True)
        nodes.append(null)

        self[:] = nodes
        if not nodes:
            return

        self.log.info(">>> containerising [ {} ]".format(name))
        return containerise(
            name=name,
            namespace=namespace,
            nodes=nodes,
            context=context,
            loader=self.__class__.__name__)

    def remove(self, container):
        """Remove RenderSetup settings instance."""
        from maya import cmds

        container_name = container["objectName"]

        self.log.info("Removing '%s' from Maya.." % container["name"])

        container_content = cmds.sets(container_name, query=True)
        nodes = cmds.ls(container_content, long=True)

        nodes.append(container_name)

        try:
            cmds.delete(nodes)
        except ValueError:
            # Already implicitly deleted by Maya upon removing reference
            pass

    def update(self, container, context):
        """Update RenderSetup setting by overwriting existing settings."""
        lib.show_message(
            "Render setup update",
            "Render setup setting will be overwritten by new version. All "
            "setting specified by user not included in loaded version "
            "will be lost.")
        repre_entity = context["representation"]
        path = get_representation_path(repre_entity)
        with open(path, "r") as file:
            try:
                renderSetup.instance().decode(
                    json.load(file), renderSetup.DECODE_AND_OVERWRITE, None)
            except Exception:
                self.log.error("There were errors during loading")
                six.reraise(*sys.exc_info())

        # Update metadata
        node = container["objectName"]
        cmds.setAttr("{}.representation".format(node),
                     repre_entity["id"],
                     type="string")
        self.log.info("... updated")

    def switch(self, container, context):
        """Switch representations."""
        self.update(container, context)
