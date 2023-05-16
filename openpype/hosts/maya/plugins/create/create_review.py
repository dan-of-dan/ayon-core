import json

from maya import cmds

from openpype.hosts.maya.api import (
    lib,
    plugin
)
from openpype.lib import (
    BoolDef,
    NumberDef,
    EnumDef
)
from openpype.settings import get_project_settings
from openpype.pipeline import (
    get_current_project_name, get_current_task_name, CreatedInstance
)
from openpype.client import get_asset_by_name

TRANSPARENCIES = [
    "preset",
    "simple",
    "object sorting",
    "weighted average",
    "depth peeling",
    "alpha cut"
]


class CreateReview(plugin.MayaCreator):
    """Playblast reviewable"""

    identifier = "io.openpype.creators.maya.review"
    label = "Review"
    family = "review"
    icon = "video-camera"

    useMayaTimeline = True
    panZoom = False

    # Overriding "create" method to prefill values from settings.
    def create(self, subset_name, instance_data, pre_create_data):

        members = list()
        if pre_create_data.get("use_selection"):
            members = cmds.ls(selection=True)

        project_name = self.project_name
        asset_doc = get_asset_by_name(project_name, instance_data["asset"])
        task_name = instance_data["task"]
        preset = lib.get_capture_preset(
            task_name,
            asset_doc["data"]["tasks"][task_name]["type"],
            subset_name,
            self.project_settings,
            self.log
        )
        self.log.debug(
            "Using preset: {}".format(
                json.dumps(preset, indent=4, sort_keys=True)
            )
        )

        with lib.undo_chunk():
            instance_node = cmds.sets(members, name=subset_name)
            instance_data["instance_node"] = instance_node
            instance = CreatedInstance(
                self.family,
                subset_name,
                instance_data,
                self)
            self._add_instance_to_context(instance)

            self.imprint_instance_node(instance_node,
                                       data=instance.data_to_store())
            return instance

    def get_instance_attr_defs(self):

        defs = lib.collect_animation_defs()

        # Option for using Maya or asset frame range in settings.
        if not self.useMayaTimeline:
            # Update the defaults to be the asset frame range
            frame_range = lib.get_frame_range()
            defs_by_key = {attr_def.key: attr_def for attr_def in defs}
            for key, value in frame_range.items():
                if key not in defs_by_key:
                    raise RuntimeError("Attribute definition not found to be "
                                       "updated for key: {}".format(key))
                attr_def = defs_by_key[key]
                attr_def.default = value

        defs.extend([
            NumberDef("review_width",
                      label="Review width",
                      tooltip="A value of zero will use the asset resolution.",
                      decimals=0,
                      minimum=0,
                      default=0),
            NumberDef("review_height",
                      label="Review height",
                      tooltip="A value of zero will use the asset resolution.",
                      decimals=0,
                      minimum=0,
                      default=0),
            BoolDef("keepImages",
                    label="Keep Images",
                    tooltip="Whether to also publish along the image sequence "
                            "next to the video reviewable.",
                    default=False),
            BoolDef("isolate",
                    label="Isolate render members of instance",
                    tooltip="When enabled only the members of the instance "
                            "will be included in the playblast review.",
                    default=False),
            BoolDef("imagePlane",
                    label="Show Image Plane",
                    default=True),
            EnumDef("transparency",
                    label="Transparency",
                    items=TRANSPARENCIES),
            BoolDef("panZoom",
                    label="Enable camera pan/zoom",
                    default=True),
            EnumDef("displayLights",
                    label="Display Lights",
                    items=lib.DISPLAY_LIGHTS_LABELS),
        ])

        return defs
