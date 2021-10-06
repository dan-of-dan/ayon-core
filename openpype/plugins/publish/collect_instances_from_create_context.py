"""Create instances based on CreateContext.

"""
import os
import pyblish.api

from openpype.lib import ApplicationManager


class CollectInstancesFromCreateContext(pyblish.api.ContextPlugin):
    """Collect instances from CreateContext from new publishing."""

    label = "Collect Instances from Create Context"
    order = pyblish.api.CollectorOrder - 0.5

    def process(self, context):
        create_context = context.data.pop("create_context", None)
        if not create_context:
            return

        for created_instance in create_context.instances:
            instance_data = created_instance.data_to_store()
            if instance_data["active"]:
                self.create_instance(context, instance_data)

    def create_instance(self, context, in_data):
        subset = in_data["subset"]
        # If instance data already contain families then use it
        instance_families = in_data.get("families") or []

        instance = context.create_instance(subset)
        instance.data.update({
            "subset": subset,
            "asset": in_data["asset"],
            "label": subset,
            "name": subset,
            "family": in_data["family"],
            "families": instance_families
        })
        for key, value in in_data.items():
            if key not in instance.data:
                instance.data[key] = value
        self.log.info("collected instance: {}".format(instance.data))
        self.log.info("parsing data: {}".format(in_data))

        instance.data["representations"] = list()
