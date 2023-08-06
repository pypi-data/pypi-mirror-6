#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""about how to produce a stopwords list"""

from os import path
from nltk.corpus import stopwords as nltk_corpus_stopwords
from .helper import read_file

def stopwords(language="smart", data_file_path="", encoding="utf-8"):
    """return a list of the stopwords.
    the package defaultly has some languages predifned.
    users can load another stopwords file with the specific file encoding
    """
    if data_file_path == "":
        the_tmpy_misc_path = path.join(path.dirname(path.realpath(__file__)), 'misc')
        data_file_path = path.join(the_tmpy_misc_path, "stopwords", (language+".dat").lower())
    #print(data_file_path)
    words = []
    file_content = read_file(data_file_path, encoding).strip('\n')
    words = file_content.split("\n")
    return words
