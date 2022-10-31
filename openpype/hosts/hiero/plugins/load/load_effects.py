import json
from collections import OrderedDict
from pprint import pprint
import six

from openpype.pipeline import (
    AVALON_CONTAINER_ID,
    load
)
from openpype.hosts.hiero import api as phiero


class LoadEffects(load.LoaderPlugin):
    """Loading colorspace soft effect exported from nukestudio"""

    representations = ["effectJson"]
    families = ["effect"]

    label = "Load Effects"
    order = 0
    icon = "cc"
    color = "white"
    ignore_attr = ["useLifetime"]

    def load(self, context, name, namespace, data):
        """
        Loading function to get the soft effects to particular read node

        Arguments:
            context (dict): context of version
            name (str): name of the version
            namespace (str): asset name
            data (dict): compulsory attribute > not used

        Returns:
            nuke node: containerised nuke node object
        """
        active_sequence = phiero.get_current_sequence()
        active_track = phiero.get_current_track(
            active_sequence, "LoadedEffects")

        # get main variables
        version = context["version"]
        version_data = version.get("data", {})
        vname = version.get("name", None)
        namespace = namespace or context["asset"]["name"]
        object_name = "{}_{}".format(name, namespace)
        clip_in = context["asset"]["data"]["clipIn"]
        clip_out = context["asset"]["data"]["clipOut"]

        data_imprint = {
            "source": version_data["source"],
            "version": vname,
            "author": version_data["author"],
            "objectName": object_name,
            "children_names": []
        }

        # getting file path
        file = self.fname.replace("\\", "/")

        # getting data from json file with unicode conversion
        with open(file, "r") as f:
            json_f = {self.byteify(key): self.byteify(value)
                      for key, value in json.load(f).items()}

        # get correct order of nodes by positions on track and subtrack
        nodes_order = self.reorder_nodes(json_f)

        used_subtracks = {
            stitem.name(): stitem
            for stitem in phiero.flatten(active_track.subTrackItems())
        }

        loaded = False
        for index_order, (ef_name, ef_val) in enumerate(nodes_order.items()):
            pprint("_" * 100)
            pprint(ef_name)
            pprint(ef_val)
            new_name = "{}_loaded".format(ef_name)
            if new_name not in used_subtracks:
                effect_track_item = active_track.createEffect(
                    effectType=ef_val["class"],
                    timelineIn=clip_in,
                    timelineOut=clip_out,
                    subTrackIndex=index_order

                )
                effect_track_item.setName(new_name)
                node = effect_track_item.node()
                for knob_name, knob_value in ef_val["node"].items():
                    if (
                        not knob_value
                        or knob_name == "name"
                    ):
                        continue

                    try:
                        node[knob_name].setValue(knob_value)
                    except NameError:
                        self.log.warning("Knob: {} cannot be set".format(
                            knob_name))

                # register all loaded children
                data_imprint["children_names"].append(new_name)
                # make sure containerisation will happen
                loaded = True

        if not loaded:
            return

        self.containerise(
            active_track,
            name=name,
            namespace=namespace,
            object_name=object_name,
            context=context,
            loader=self.__class__.__name__,
            data=data_imprint)

    def update(self, container, representation):
        """Update the Loader's path

        Nuke automatically tries to reset some variables when changing
        the loader's path to a new file. These automatic changes are to its
        inputs:

        """
        pass

    def reorder_nodes(self, data):
        new_order = OrderedDict()
        trackNums = [v["trackIndex"] for k, v in data.items()
                     if isinstance(v, dict)]
        subTrackNums = [v["subTrackIndex"] for k, v in data.items()
                        if isinstance(v, dict)]

        for trackIndex in range(
                min(trackNums), max(trackNums) + 1):
            for subTrackIndex in range(
                    min(subTrackNums), max(subTrackNums) + 1):
                item = self.get_item(data, trackIndex, subTrackIndex)
                if item is not {}:
                    new_order.update(item)
        return new_order

    def get_item(self, data, trackIndex, subTrackIndex):
        return {key: val for key, val in data.items()
                if isinstance(val, dict)
                if subTrackIndex == val["subTrackIndex"]
                if trackIndex == val["trackIndex"]}

    def byteify(self, input):
        """
        Converts unicode strings to strings
        It goes through all dictionary

        Arguments:
            input (dict/str): input

        Returns:
            dict: with fixed values and keys

        """

        if isinstance(input, dict):
            return {self.byteify(key): self.byteify(value)
                    for key, value in input.items()}
        elif isinstance(input, list):
            return [self.byteify(element) for element in input]
        elif isinstance(input, six.text_type):
            return str(input)
        else:
            return input

    def switch(self, container, representation):
        self.update(container, representation)

    def remove(self, container):
        pass

    def containerise(
        self,
        track,
        name,
        namespace,
        object_name,
        context,
        loader=None,
        data=None
    ):
        """Bundle Hiero's object into an assembly and imprint it with metadata

        Containerisation enables a tracking of version, author and origin
        for loaded assets.

        Arguments:
            track (hiero.core.VideoTrack): object to imprint as container
            name (str): Name of resulting assembly
            namespace (str): Namespace under which to host container
            object_name (str): name of container
            context (dict): Asset information
            loader (str, optional): Name of node used to produce this
                                    container.

        Returns:
            track_item (hiero.core.TrackItem): containerised object

        """

        data_imprint = {
            object_name: {
                "schema": "openpype:container-2.0",
                "id": AVALON_CONTAINER_ID,
                "name": str(name),
                "namespace": str(namespace),
                "loader": str(loader),
                "representation": str(context["representation"]["_id"]),
            }
        }

        if data:
            for k, v in data.items():
                data_imprint[object_name].update({k: v})

        self.log.debug("_ data_imprint: {}".format(data_imprint))
        phiero.set_track_openpype_tag(track, data_imprint)
