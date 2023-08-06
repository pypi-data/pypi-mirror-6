#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""This is all about Source"""

from os import path
import os
import sys
import pandas as pd


def get_sources():
    return ["DirSource", "VectorSource"]


class Source(object):
    def __init__(self,
        defaultReader = None,
        encoding = "utf-8",
        length = None,
        names = None,
        position = 0,
        vectorized = True):
        self.defaultReader = defaultReader
        self.encoding = encoding
        self.length = length
        self.names = names
        self.position = position
        self.vectorized = vectorized

    def get_info(self):
        pass

    def get_resources(self):
        pass


class VectorSource(Source):
    """A vector where each component is interpreted as document"""
    def __init__(self,
        x,
        defaultReader = None,
        encoding = "utf-8",
        length = None,
        names = None,
        position = 0,
        vectorized = True):
        Source.__init__(self,
        defaultReader,
        encoding,
        length,
        names,
        position,
        vectorized)
        self.length = len(x)
        self.content = x

    def get_info(self):
        return {"encoding": self.encoding,
            "names": self.names,
            "vectorized": self.vectorized,
            "type": "string"}

    def get_resources(self):
        return self.content

    def __len__(self):
        return self.length


# class DataframeSource(Source):
#     """A data frame where each row is interpreted as document"""
#     def __init__(self,
#         x = pd.DataFrame(),
#         defaultReader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         defaultReader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         self.content = x
#         self.length = len(self.content)
#     pass


class DirSource(Source):
    """A directory with files"""
    def __init__(self,
        directory = ".",
        defaultReader = None,
        encoding = "utf-8",
        length = None,
        names = None,
        position = 0,
        vectorized = True,
        pattern = None,
        recursive = False,
        ignore_case = False):
        Source.__init__(self,
        defaultReader = None,
        encoding = "utf-8",
        length = None,
        names = None,
        position = 0,
        vectorized = True)
        if not path.isdir(path.expanduser(directory)):
            sys.exit('not a dir')
        self.directory = directory
        self.pattern = pattern
        self.recursive = recursive
        self.ignore_case = ignore_case
        self.FileList = []
        self.names = []
        for (dir_path, dir_names, file_names) in os.walk(self.directory):
            self.names.extend(file_names)
            self.FileList.extend([path.join(dir_path, file_name) for file_name in file_names])
            if not self.recursive:
                break
        self.length = len(self.names)

    def get_info(self):
        return {"encoding": self.encoding,
            "length": self.length,
            "names": self.names,
            "vectorized": self.vectorized,
            "type": "filename"}

    def get_resources(self):
        return self.FileList

    def __len__(self):
        return self.length


# class URISource(Source):
#     """Documents identified by a Uniform Resource Identifier"""
#     def __init__(self,
#         x,
#         defaultReader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         defaultReader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         self.x = x
#     pass

# class ReutersSource(Source):
#     def __init__(self,
#         x,
#         defaultReader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         defaultReader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         self.x = x
#     pass


# class XMLSource(Source):
#     """XML"""
#     def __init__(self,
#         x,
#         parser,
#         reader,
#         defaultReader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         defaultReader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         self.x = x
#         self.parser = parser
#         self.reader = reader
#     pass

# def eoi(x):
#     pass

# def eoi_Source(x):
#     pass
