#! /usr/bin/env python
#-*- coding : utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

"""
    Utilities for Microbe app 
"""

__author__ = 'TROUVERIE Joachim'

from itertools import islice
from flask import abort

def get_objects_for_page(objects, page, per_page) :
    """
    Calculate indexes to paginate object lists
    """
    # check if list is empty
    if not objects :
        return []
    # calculate index
    index_min = (page - 1) * per_page
    # if index minimum is more than objects length
    if index_min > len(objects) - 1 :
        abort(404)
    index_max = per_page * page
    # return a sliced list
    return list(islice(objects, index_min, index_max))
