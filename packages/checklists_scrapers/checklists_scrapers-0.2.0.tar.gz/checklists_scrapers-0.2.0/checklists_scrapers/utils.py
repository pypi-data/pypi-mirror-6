"""Utility functions used across the application."""

import os


def list_files(root_dir, ext):
    """Return the list of files in a directory tree with a given extension.

    Args:
        root_dir (str): the path to the root directory.
        ext (str): the file extension

    Returns:
        list(str): a list of paths to the files in the directory tree with
        the matching file extension.
    """
    paths = []
    for path, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith(ext):
                paths.append(os.path.join(path, filename))
    return paths
