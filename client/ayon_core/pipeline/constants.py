# Metadata ID of loaded container into scene
AYON_CONTAINER_ID = "ayon.load.container"
AYON_INSTANCE_ID = "ayon.create.instance"
# Backwards compatibility
AVALON_CONTAINER_ID = "pyblish.avalon.container"
AVALON_INSTANCE_ID = "pyblish.avalon.instance"

# TODO get extensions from host implementations
HOST_WORKFILE_EXTENSIONS = {
    "blender": [".blend"],
    "celaction": [".scn"],
    "tvpaint": [".tvpp"],
    "fusion": [".comp"],
    "harmony": [".zip"],
    "houdini": [".hip", ".hiplc", ".hipnc"],
    "maya": [".ma", ".mb"],
    "nuke": [".nk",".nkind"],
    "hiero": [".hrox"],
    "photoshop": [".psd", ".psb"],
    "premiere": [".prproj"],
    "resolve": [".drp"],
    "aftereffects": [".aep"]
}
