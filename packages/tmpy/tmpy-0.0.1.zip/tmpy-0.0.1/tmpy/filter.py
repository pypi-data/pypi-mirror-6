#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""all about filter"""

from .corpus import Corpus


def tm_filter(x, func, *args, **kwargs):
    """
    Filter the documents based on the filter func with parameters.

    Parameters
    ===========
    x: Corpus like object.
        x should be iterable.
    func: a function or callable.
        For example, s_filter that comes with this package.
    *args: arguments.
        *args would be passed to func.
    **kwargs: key words arguments
        **kwargs would be passed to func.

    Returns
    ========
    result: a new Corpus.
        A new Corpus, all documents of which satisfies the filter function.
    """
    result = Corpus()
    result.meta = x.get_meta()
    for doc in x:
        if func(doc, *args, **kwargs):
            #TODO do not use hack here in the future
            result.docs = result.docs + [doc]
    return result


def s_filter(doc, conditions=None):
    """
    It check whether the document satisfy the dict-like conditions and return True or False

    Parameters
    ===========
    doc: Document like object.
        For example, a PlainTextDocument project.
    conditions: a python dict object, meaning the meta data.
        For example, {"ID": 3, "Author": "Albert"}

    Returns
    =======
    result: boolean, {True, False}.
        If the document has the meta data, the function returns True. Else returns False.

    """
    if conditions is None:
        return False
    predefinedmetadatas = ["Name", "Author", "DateTimeStamp", "Description", "ID", "Origin", "Heading", "Language"]
    for item in conditions:
        if item in predefinedmetadatas:
            if not doc.get_predefinedmetadata(item) == conditions[item]:
                return False
        else:
            try:
                value = doc.get_localmetadata(item)
            except KeyError:
                return False
            if not value == conditions[item]:
                return False
    return True
