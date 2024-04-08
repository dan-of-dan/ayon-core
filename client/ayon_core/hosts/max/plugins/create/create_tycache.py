# -*- coding: utf-8 -*-
"""Creator plugin for creating TyCache."""
from ayon_core.hosts.max.api import plugin


class CreateTyCache(plugin.MaxCreator):
    """Creator plugin for TyCache."""
    identifier = "io.openpype.creators.max.tycache"
    label = "TyCache"
    product_type = "tycache"
    icon = "gear"


class CreateTySpline(plugin.MaxCreator):
    """Creator plugin for TyCache."""
    identifier = "io.openpype.creators.max.tyspline"
    label = "TyCache (TySpline)"
    family = "tyspline"
    icon = "gear"
    # TODO: get the operator here and divide into
    # new creators instead if multiple operator involved here.