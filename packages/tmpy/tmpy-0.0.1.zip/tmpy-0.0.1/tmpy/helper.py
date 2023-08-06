#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)


"""many helpers and variables for the package"""

import os
import codecs
import inspect
from collections import OrderedDict
from datetime import datetime
from HTMLParser import HTMLParser
from scipy.sparse import coo_matrix
from xmltodict import unparse


def current_date_time():
    return datetime.now().time()


def read_file(file_name, encoding='utf-8'):
    with codecs.open(file_name, 'r', encoding=encoding) as f:
        text = f.read()
    return text


def write_file(text, file_name, encoding='utf-8'):
    with codecs.open(file_name,'w',encoding='utf8') as f:
        f.write(text)
    return True


def list_of_lists_to_flat_list(list_of_lists):
    """magically turn a list of lists into a flat list.

    Parameters
    ==========
    list_of_lists: list of lists
        for example, [["i", "think", "i", "am", "ok"], ["yes", "you", "are", "ok"]]

    Returns
    ==========
    a flat list.
        for example, ["i", "think", "i", "am", "ok", "yes", "you", "are", "ok"]

    """

    flat_list = [item for inside_list in list_of_lists for item in inside_list]
    return flat_list


def sparse_data_frame_to_sparse_matrix(df):
    """turn the pandas.DataFrame to a scipy.sparse.coo_matrix"""
    return coo_matrix(df.values)


def raw_text_from_xmltodict_obj(parsed_obj):
    return unparse(OrderedDict([('xml', parsed_obj)]))[44:-6]


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
