#! /usr/bin/env python
#-*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

"""
    Admin views for Microbe app 
"""

__author__ = 'TROUVERIE Joachim'

import os
import os.path as op
from datetime import datetime
from werkzeug import secure_filename
from microbe import pages
from models import Users, Content, File
from search import update_document, delete_document
from forms import LoginForm, UserForm, ConfigForm, ContentForm
from utils import get_objects_for_page
from flask import (Blueprint, url_for, redirect, current_app, request,
                   render_template, session)
from flask.ext.themes2 import get_themes_list
from flask.ext.silk import Silk
from flask.ext.paginate import Pagination
from flask.ext.babel import lazy_gettext, refresh
from flask.ext.login import login_user, logout_user, login_required


bp = Blueprint('admin', __name__)
silk = Silk(bp)


def load_user(username) :
    """
    Load user from config
    """
    # get config
    config = current_app.config['USERS']
    return Users.get(username)


def save_config() :
    """
    Save config in file
    """
    config = current_app.config
    path = op.join(current_app.root_path, 'settings.py')
    with open(path, 'w+') as config_file :
        for key, value in config.iteritems() :
            if isinstance(value, unicode) or isinstance(value, str):
                content = "{0} = u'{1}'".format(key, value)
            elif callable(value) :
                pass
            else :
                content = "{0} = {1}".format(key, value)
            # add new line
            content += '\n'
            # write
            config_file.write(content.encode('utf-8'))


@bp.route('/')
@login_required
def index() :
    """
    Admin index view
    """
    return render_template('admin/index.html')


@bp.route('/login', methods = ['GET', 'POST'])
def login() :
    """
    Login view
    """
    # create form
    form = LoginForm()
    # form submit
    if form.validate_on_submit() :
        # check username and password
        user = Users.get(form.username.data)
        if not user :
            form.username.errors.append(lazy_gettext(u'Invalid user'))
        elif not user.check_password(form.password.data) :
            form.password.errors.append(lazy_gettext(u'Invalid password'))
        else :
            login_user(user, remember = form.remember.data)
            return redirect(url_for('.index'))
    return render_template('admin/model.html', form = form, 
            url = url_for('.login'))


@bp.route('/logout')
@login_required
def logout() :
    """
    Logout user
    """
    logout_user()
    return redirect(url_for('index'))


@bp.route('/config', methods = ['GET', 'POST'])
@login_required
def config() :
    """
    Edit config
    """
    # get config
    config = current_app.config
    # populate form with config
    form = ConfigForm(
            sitename = config.get(u'SITENAME'),
            subtitle = config.get(u'SUBTITLE'),
            author = config.get(u'AUTHOR'),
            language = config.get(u'LANGUAGE'),
            pagination = config.get(u'PAGINATION'),
            summary_length = config.get(u'SUMMARY_LENGTH'),
            comments = config.get(u'COMMENTS'),
            rss = config.get(u'RSS'),
            recaptcha_public_key = config.get(u'RECAPTCHA_PUBLIC_KEY'),
            recaptcha_private_key = config.get(u'RECAPTCHA_PRIVATE_KEY')
            )
    if form.validate_on_submit() :
        # update config
        form.populate_obj(config)
        # refresh babel
        if config.get(u'LANGUAGE') != current_app.config.get(u'LANGUAGE') :
            refresh()
        current_app.config.update(config)
        # save config
        save_config()
        return redirect(url_for('admin.index'))
    return render_template('admin/model.html', 
            form = form, 
            title = lazy_gettext(u'Configuration of ') + 
            config.get(u'SITENAME'),
            url = url_for('.config'))


@bp.route('/users/')
@login_required
def users() :
   """
   List users
   """
   # get config
   users = current_app.config[u'USERS']
   lst = users.keys()
   # pagination
   try :
       page = int(request.args.get('page', 1))
   except ValueError :
       page = 1
   per_page = 10
   pagination = Pagination(page = page, 
                           total = len(lst), 
                           search = False,
                           per_page = per_page,
                           css_framework='foundation')
   displayed = get_objects_for_page(lst, page, per_page)
   return render_template('admin/users.html', users = displayed, 
           pagination = pagination)


@bp.route('/user/<user>', methods = ['GET', 'POST'])
@bp.route('/user/', methods = ['GET', 'POST'])
@login_required
def user(user = None) :
    """
    Edit or create user
    """
    # get user
    if user :
        form = UserForm(username = user)
        title = user
    else :
        form = UserForm()
        title = lazy_gettext(u'New user')
    if form.validate_on_submit() :
        # update or add new user
        username = form.username.data
        pwd = form.password.data
        Users.update(username, pwd)
        save_config()
        return redirect(url_for('admin.users'))
    return render_template('admin/model.html', title = title, 
            form = form, url = url_for('.user'))


@bp.route('/delete_user/<user>/', methods = ['DELETE'])
@login_required
def delete_user(user) :
    """
    Delete user
    """
    Users.delete(user)
    save_config()
    return redirect(url_for('users'))


@bp.route('/contents/')
@login_required
def contents() :
    """
    List posts
    """
    contents = [Content.from_page(p) for p in pages]
    sorted_contents = sorted(contents, 
                             key = lambda x : x.published,
                             reverse = True)
    # pagination
    try :
        page = int(request.args.get('page', 1))
    except ValueError :
        page = 1
    per_page = 10
    pagination = Pagination(page = page, 
                           total = len(sorted_contents), 
                           search = False,
                           per_page = per_page,
                           css_framework='foundation')
    displayed = get_objects_for_page(sorted_contents, page, per_page)
    return render_template('admin/contents.html', pages = displayed, 
            pagination = pagination)


@bp.route('/content/<path:path>/', methods = ['GET', 'POST'])
@bp.route('/content/', methods = ['GET', 'POST'])
@login_required
def content(path = None) :
    """
    Edit or create post
    """    
    # edit post
    if path :
        title = lazy_gettext(u'Edit content')
        page = pages.get(path)
        content = Content.from_page(page)
    else :
        content = Content()
        title = lazy_gettext(u'New content')
    # populate form
    form = ContentForm(obj = content)
    if form.validate_on_submit() :
        form.populate_obj(content)
        content.save()
        update_document(content)
        return redirect(url_for('.contents'))
    # new post
    return render_template('admin/content.html', title = title, 
            url = url_for('.content'), form = form)


@bp.route('/delete_content/<path:path>/', methods = ['POST'])
@login_required
def delete_content(path) :
    """
    Delete content 
    """
    page = pages.get(path)
    content = Content.from_page(page)
    content.delete()
    delete_document(content)
    return redirect(url_for('.contents'))


@bp.route('/publish_content/<path:path>/', methods = ['POST'])
@login_required
def publish_content(path) :
    """
    Publish content 
    """
    page = pages.get(path)
    content = Content.from_page(page)
    content.draft = False
    content.published = datetime.now()
    content.save()
    update_document(content)
    return redirect(url_for('.contents'))


@bp.route('/media/')
@login_required
def media() :
    """
    List media available to contents
    """
    path = op.join(op.abspath(op.dirname(__file__)), 'static', 'media')
    if not op.exists(path) :
        os.makedirs(path)
    files = [File(f) for f in os.listdir(path)]
    # pagination
    try :
        page = int(request.args.get('page', 1))
    except ValueError :
        page = 1
    per_page = 10
    pagination = Pagination(page = page, 
                           total = len(files), 
                           search = False,
                           per_page = per_page,
                           css_framework='foundation')
    displayed = get_objects_for_page(files, page, per_page)
    return render_template('admin/media.html', files = displayed, 
            pagination = pagination)


@bp.route('/upload/', methods = ['POST'])
@login_required
def upload() :
    """
    Upload new file
    """
    path = op.join(op.abspath(op.dirname(__file__)), 'static', 'media')
    fi = request.files[u'file']
    if fi :
        filename = secure_filename(fi.filename)
        path = op.join(path, filename)
        fi.save(path)
        obj = File(filename)
        return redirect(url_for('.media')) 
    return None


@bp.route('/delete_media/<slug>/', methods = ['POST'])
@login_required
def delete_media(slug) :
    """
    Delete file
    """
    path = op.join(op.abspath(op.dirname(__file__)), 'static', 'media')
    for fi in os.listdir(path) :
        obj = File(fi)
        if obj.slug == slug :
            filepath = op.join(path, obj.name)
            os.remove(filepath)
    return redirect(url_for('.media'))


@bp.route('/themes/')
@login_required
def themes() :
    """
    List available themes
    """
    current_app.theme_manager.refresh()
    themes = get_themes_list()
    selected = session.get(u'theme', current_app.config[u'DEFAULT_THEME'])
    return render_template('admin/themes.html', themes = themes, 
            selected = selected)


@bp.route('/themes/<ident>')
@login_required
def set_theme(ident):
    """
    Set theme using session
    """
    if ident not in current_app.theme_manager.themes :
        abort(404)
    session[u'theme'] = ident
    return redirect(url_for('.themes'))
