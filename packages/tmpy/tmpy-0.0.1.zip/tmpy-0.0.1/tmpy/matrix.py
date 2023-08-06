#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""all about DocumentTermMatrix and TermDocumentMatrix"""

from numpy import ceil
from .weight import weight_tf
from .tokenizer import nltk_word_tokenize
from .corpus import Corpus
from .transform import tm_map_content_list


def build_term_document_matrix(x, dictionary=None, weighting=None, tockenizer=None):
    """generate a term document matrix"""
    if weighting is None:
        weighting = weight_tf
    if tockenizer is None:
        tockenizer = nltk_word_tokenize
    list_of_list_of_terms = tm_map_content_list(x, tockenizer)
    list_of_doc_names = []
    for item in x:
        list_of_doc_names = list_of_doc_names + [item.get_predefinedmetadata("Name")]
    result = weighting(list_of_list_of_terms, dictionary)
    result.columns = list_of_doc_names
    return result


def build_document_term_matrix(x, dictionary=None, weighting=None, tockenizer=None):
    """generate a document term matrix"""
    if weighting is None:
        weighting = weight_tf
    if tockenizer is None:
        tockenizer = nltk_word_tokenize
    return (build_term_document_matrix(x, dictionary, weighting, tockenizer)).transpose()


def find_frequent_terms_in_tdm(tdm, n=1):
    """find the terms occurs at least n times in a term document matrix"""
    return find_frequent_terms_in_dtm(tdm.transpose(), n)


def find_frequent_terms_in_dtm(dtm, n=1):
    """find the terms occurs at least n times in a document term matrix"""
    freq_of_terms_sum = dtm.sum()
    return freq_of_terms_sum[freq_of_terms_sum > (n - 1)].index.tolist()


def find_associations_in_tdm(tdm, term, correlation):
    """find the terms which correlate with the parameter term with at least parametr correlation"""
    #TODO
    return find_associations_in_dtm(tdm.transpose(), term, correlation)


def find_associations_in_dtm(dtm, term, correlation):
    """find the terms which correlate with the parameter term with at least parametr correlation"""
    #TODO
    correlations_of_the_term = dtm.corr()[term]
    return correlations_of_the_term[correlations_of_the_term>correlation].dropna().drop([term])


def remove_sparse_terms_in_tdm(tdm, term_sparsity):
    return remove_sparse_terms_in_dtm(tdm.transpose(), term_sparsity)


def remove_sparse_terms_in_dtm(dtm, term_sparsity):
    docs_count = dtm.shape[0]
    occurence_limit = ceil(docs_count * term_sparsity)
    to_be_removed_terms_list = []
    for term in dtm:
        every_value_counts = dtm[term].to_dense().value_counts()
        if (0 in every_value_counts) and (every_value_counts[0] >= occurence_limit):
            to_be_removed_terms_list = to_be_removed_terms_list + [term]
        else:
            continue
    terms_removed_dtm = dtm.drop(to_be_removed_terms_list, 1)
    result = terms_removed_dtm.to_dense().loc[~(terms_removed_dtm.to_dense() == 0).all(axis=1)].to_sparse(fill_value=0)
    return result
