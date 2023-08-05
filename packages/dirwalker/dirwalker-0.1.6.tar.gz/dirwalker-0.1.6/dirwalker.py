#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 The dirwalker developers. All rights reserved.
# Project site: https://github.com/matthewrankin/dirwalker
# Use of this source code is governed by a MIT-style license that
# can be found in the LICENSE.txt file for the project.
"""Walk a directory searching for certain file extensions.

This package will walk multiple-level directories searching for files with the
given extensions.
"""

# Try to future proof code so that it's Python 3.x ready
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# Standard module imports
import os

# The version as used in the setup.py
__version__ = '0.1.6'


def find_filenames_with_extensions(
        search_directory, extensions):
    """Find filenames with given extensions.

    Args:
        search_directory: A string of the absolute or relative directory to
            search.
        extensions: A list or tuple of strings containing the extensions to
            look for.

    Returns:
        A list of filenames found.
    """
    files_found = []
    search_directory = os.path.abspath(search_directory)
    for root, dirs, files in os.walk(search_directory):
        for filename in files:
            current_file = os.path.join(root, filename)
            for extension in extensions:
                if filename.endswith(extension):
                    files_found.append(current_file)
    return files_found
