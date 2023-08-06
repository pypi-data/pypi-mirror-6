#! /usr/bin/env python
#-*- coding : utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

"""
   Config for Microbe app 
"""

__author__ = 'TROUVERIE Joachim'

from werkzeug.security import generate_password_hash
from uuid import uuid4

PERMANENT_SESSION_LIFETIME = 31
LANGUAGE = u'en'
SITENAME = u'Microbe Default site'
USERS = {u'admin' : generate_password_hash(u'microbe')}
FLATPAGES_ROOT = u'content'
POST_DIR = u'posts'
PAGE_DIR = u'pages'
PAGINATION = 5
SUMMARY_LENGTH = 300
FLATPAGES_EXTENSION = u'.md'
FLATPAGES_AUTO_RELOAD = True
COMMENTS = u'NO'
RSS = u'NO'
DEFAULT_THEME = u'dark'
SECRET_KEY = uuid4().hex
