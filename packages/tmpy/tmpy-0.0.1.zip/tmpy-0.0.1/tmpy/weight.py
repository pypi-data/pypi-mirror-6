#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""all the package built-in weight functions"""

from collections import Counter
from numpy import log
import pandas as pd


def get_weight_functions():
    return ["weight_tf", "weight_tf_idf"]


def weight_tf(x, dictionary=None):
    """generate the term frequency based on the input documents tokens list.

    Parameters
    ==========
    x: list of the documents tokens
        for example, [["i", "think", "i", "am", "ok"], ["yes", "you", "are", "ok"]]
    dictionary: None (default) or list of the tokens to be built in the tf matrix
        for example, None or ["ok","yes"]

    Returns
    ==========
    a sparse DataFrame of the term document matrix

    """
    #TODO try to find out a memory friendly solution
    if dictionary is None:
        y = [Counter(item) for item in x]
    else:
        y = [Counter({k:v for k,v in Counter(item).iteritems() if k in dictionary}) for item in x]
    z = [pd.Series(item.values(), index=item.keys(), dtype='int64') for item in y]
    result = pd.concat(z, axis=1).fillna(0).to_sparse(fill_value=0)
    return result


def weight_tf_idf(x, dictionary=None, smooth=False):
    """generate the term frequency–inverse document frequency based on the input documents tokens list.

    Parameters
    ==========
    x: list of the documents tokens
        for example, [["i", "think", "i", "am", "ok"], ["yes", "you", "are", "ok"]]
    dictionary: None (default) or list of the tokens to be built in the tf-idf matrix
        for example, None or ["ok","yes"]

    Returns
    ==========
    a sparse DataFrame of the term frequency–inverse document frequency matrix

    """
    #TODO try to find out a memory friendly solution
    docs_counts = len(x)
    smoothness = 1 if smooth else 0
    tf_dtm = (weight_tf(x, dictionary)).transpose().to_dense()
    terms_occured_docs_count = docs_counts - (tf_dtm==0).sum()
    idf_terms = log(docs_counts / terms_occured_docs_count)
    idf_dtm = tf_dtm * idf_terms
    idf_tdm = idf_dtm.transpose().to_sparse(fill_value=0)
    return idf_tdm #return the tdm, not the dtm
