# -*- coding: utf-8 -*-
"""
Safe lookup helpers for required ANSYS objects.
"""

import System


def get_single_object_by_name(name, context="analysis workflow"):
    """Return the first object with a given name or raise a clear exception."""
    objects = DataModel.GetObjectsByName(name)
    if not objects:
        raise System.Exception(
            "Required object '{0}' was not found in DataModel. "
            "This is critical for {1}. Check the model tree and ensure the object exists."
            .format(name, context)
        )
    return objects[0]


def get_first_analysis(context="analysis workflow"):
    """Return the first analysis from Model.Analyses or raise a clear exception."""
    analyses = Model.Analyses
    if not analyses or len(analyses) == 0:
        raise System.Exception(
            "No analysis system was found in Model.Analyses. "
            "This is critical for {0}. Add at least one analysis system and retry."
            .format(context)
        )
    return analyses[0]
