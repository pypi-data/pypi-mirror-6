#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""all about Document object"""

import sys


class Document(object):
    def __init__(self, x = None, name = "", author = "", datetimestamp = None,
        description = "", heading = "", doc_id = "", origin = "",
        language = "", localmetadata = None):
        self.content = x
        self.predefinedmetadata = {"Name": name,
            "Author": author,
            "DateTimeStamp": datetimestamp,
            "Description": description,
            "Heading": heading,
            "ID": doc_id,
            "Origin": origin,
            "Language": language}
        self.localmetadata = localmetadata
        if localmetadata is None:
            self.localmetadata = {}

    def get_content(self):
        return self.content

    def set_content(self, new_content):
        self.content = new_content
        return True

    def get_predefinedmetadata(self, key=None):
        if key is None:
            return self.predefinedmetadata
        else:
            return self.predefinedmetadata[key]

    def set_predefinedmetadata(self, key, value):
        self.predefinedmetadata[key] = value
        return True

    def get_localmetadata(self, key=None):
        if key is None:
            return self.localmetadata
        else:
            return self.localmetadata[key]

    def set_localmetadata(self, key, value):
        self.localmetadata[key] = value
        return True

    def inspect(self):
        print("predefinedmetadata: ")
        print(self.get_predefinedmetadata())
        print("localmetadata added by users:")
        print(self.get_localmetadata())
        print("the content of this document:")
        print(self.get_content())
        print("\n")
        return True


class PlainTextDocument(Document):
    def __init__(self, x = "", name = "", author = "", datetimestamp = None,
        description = "", heading = "", doc_id = "", origin = "",
        language = "", localmetadata = None):
        """construct a PlainTextDocument"""
        Document.__init__(self, x, name, author, datetimestamp,
            description, heading, doc_id, origin,
            language, localmetadata)
    pass


class RCV1Document(Document):
    def __init__(self, x = None, name = "", author = "", datetimestamp = None,
        description = "", heading = "", doc_id = "", origin = "",
        language = "", localmetadata = None):
        """construct a RCV1Document"""
        if x is None:
            x = []
        Document.__init__(self, x, name, author, datetimestamp,
            description, heading, doc_id, origin,
            language, localmetadata)


class Reuters21578Document(Document):
    def __init__(self, x = None, name = "", author = "", datetimestamp = None,
        description = "", heading = "", doc_id = "", origin = "",
        language = "", localmetadata = None):
        """construct a Reuters21578Document"""
        if x is None:
            x = []
        Document.__init__(self, x, name, author, datetimestamp,
            description, heading, doc_id, origin,
            language, localmetadata)

