# coding: utf-8

""" Isochrone-related functions """

# Standard library imports
import os
from glob import glob

# Third party imports
import numpy as np

isochrone_folder = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "data/isochrones")

available_types = map(os.path.basename, glob(isochrone_folder + "/*"))

__all__ = ["available_types", "open"]

def interpret_dartmouth(isochrone_contents):
    """
    Interprets a Dartmouth-style isochrone from the file contents.
    """

    formatted_isochrones = []
    base_metadata = {"SOURCE": "Dartmouth"}
    
    isochrones = "".join(isochrone_contents).split("\n\n\n")
    for i, isochrone in enumerate(isochrones):

        metadata = {}
        raw_data = isochrone.split("\n")
        if i == 0:
            # Get metadata from top of file
            keys = raw_data[2].strip("# \n\r").split()
            values = map(float, raw_data[3].strip("# \n\r").split())
            base_metadata.update(dict(zip(keys, values)))

        metadata.update(base_metadata)

        data = []
        isochrone_headers = None
        for j, line in enumerate(raw_data):
            if line.startswith("#"):
                # Add metadata
                if line.startswith("#AGE"):
                    metadata.update({
                        "AGE": float(line[5:11]),
                        "EEPS": float(line[17:])
                        })

                continue
            elif isochrone_headers is None:
                isochrone_headers = raw_data[j-1].strip("# \n\r").split()
            line_data = map(float, line.strip().split())

            if len(line_data) > 0:
                data.append(line_data)

        # Use isochrone headers
        data = np.core.records.fromarrays(np.array(data).transpose(), names=isochrone_headers, formats=['f8']*15)
        formatted_isochrones.append((data, metadata))

    return formatted_isochrones


def identify_type(filename, contents):
    return "dartmouth"


def load(filename):
    """
    Loads an isochrone from the given filename.

    Parameters
    ----------

    filename : str
    """

    # Identify what kind of isochrone this is
    with open(filename, "r") as fp:
        contents = fp.readlines()

    isochrone_type = identify_type(filename, contents)

    if isochrone_type == "dartmouth":
        interpreter = interpret_dartmouth

    else: 
        raise NotImplementedError("cannot open isochrones from {0}"
            .format(isochrone_type))

    return interpreter(contents)