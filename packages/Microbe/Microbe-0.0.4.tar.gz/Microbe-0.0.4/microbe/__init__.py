#! /usr/bin/env python
#-*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

"""
    Microbe app
"""

__author__ = 'TROUVERIE Joachim'

import os.path as op
from os import makedirs, symlink
from flask import Flask
from flask.ext.flatpages import FlatPages
from flask.ext.pagedown import PageDown
from flask.ext.login import LoginManager
from flask.ext.babel import Babel
from flask.ext.themes2 import Themes

# create app
app = Flask(__name__)

# config
path = op.join(op.dirname(__file__), 'settings.py')
if op.exists(path) :
    app.config.from_pyfile('settings.py')
else :
    app.config.from_pyfile('default_settings.py')

# create path if not exists
path =  op.join(op.dirname(__file__), 'content')
if not op.exists(path) :
    makedirs(op.join(path, 'pages'))
    makedirs(op.join(path, 'posts'))
path = op.join(op.expanduser('~'), '.microbe')
theme_path =  op.join(op.dirname(__file__), 'themes')
if not op.exists(path) :
    makedirs(path)
    symlink(theme_path, op.join(path, 'themes'))

# flatpages
pages = FlatPages(app)

# pagedown
pagedown = PageDown(app)

# login
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'admin.login'

# translations
babel = Babel(app)

# themes support
Themes(app, app_identifier = 'microbe')

# blueprint
from admin import bp as admin_module
from admin import load_user
app.register_blueprint(admin_module, url_prefix = '/admin')
lm.user_loader(load_user)

from microbe import views
