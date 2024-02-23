import os
import pyblish.api
from ayon_core.pipeline import publish
from ayon_core.hosts.zbrush.api.lib import execute_publish_model


class ExtractModelAbc(publish.Extractor):
    """
    Extract Geometry in Zbrush
    """

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract Model"
    hosts = ["zbrush"]

    def process(self, instance):

        stagingdir = self.staging_dir(instance)
        filename = "{name}.abc".format(**instance.data)
        filepath = os.path.join(stagingdir, filename)


        if "representations" not in instance.data:
            instance.data["representations"] = []

        resolve_filepath = filepath.replace("\\", "/")
        execute_publish_model(resolve_filepath)
        representation = {
            "name": "abc",
            "ext": "abc",
            "files": filename,
            "stagingDir": stagingdir,
        }

        instance.data["representations"].append(representation)
        self.log.info(
            "Extracted instance '%s' to: %s" % (instance.name, filepath)
        )