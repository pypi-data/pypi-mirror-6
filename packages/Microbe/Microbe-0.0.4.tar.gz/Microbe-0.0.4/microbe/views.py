#! /usr/bin/env python
#-*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

"""
    Views for Microbe app
"""

__author__ = 'TROUVERIE Joachim'

import os.path
from clize import clize, run
from datetime import datetime
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
from flask import g, request, abort, session
from flask.ext.paginate import Pagination
from flask.ext.babel import format_datetime, lazy_gettext
from flask.ext.themes2 import render_theme_template
from microbe import app, pages, babel
from models import Content 
from forms import CommentForm, SearchForm
from utils import get_objects_for_page
from search import search_query, init_index

def render(template, **context):
    """
    Render template with session theme
    """
    theme = session.get('theme', app.config[u'DEFAULT_THEME'])
    return render_theme_template(theme, template, **context)


def create_pagination(page, per_page, objects) :
    """
    Create pagination object
    """
    return Pagination(page = page, 
                      total = len(objects), 
                      search = False,
                      per_page = per_page,
                      css_framework='foundation')



@app.errorhandler(404)
def page_not_found(e):
    """
    Page not found error handler
    """
    return render('404.html'), 404


@babel.localeselector
def get_locale() :
    """
    Get locale for translations
    """
    return app.config.get(u'LANGUAGE')


@app.template_filter('date')
def date_filter(date, format = None) :
    if date :
        if format :
            return format_datetime(date, format)
        else :
            return format_datetime(date, 'dd MM yyyy')
    else :
        return ''


@app.before_request
def before_request() :
    # posts list
    contents = [Content.from_page(p) for p in pages]
    g.posts  = sorted(
                [c for c in contents if c.content_type == 'posts' 
                and not c.draft],
                key = lambda x : x.published,
                reverse = True
                )
    # posts categories
    g.categories = set([c.category for c in g.posts if c.category])
    # static pages
    g.static_pages = [c for c in contents if c.content_type == 'pages'
                     and not c.draft]
    if not hasattr(g, 'search_form') : 
        g.search_form = SearchForm()


@app.route('/')
def index():
    """
    List of blog posts summaries
    """
    # pagination
    try :
        page = int(request.args.get('page', 1))
    except ValueError :
        page = 1
    per_page = app.config[u'PAGINATION']    
    pagination = create_pagination(page, per_page, g.posts)
    # get content for current page
    displayed = get_objects_for_page(g.posts, page, per_page)
    # override page to have summary
    return render('index.html', pages=displayed, pagination=pagination)


@app.route('/<path:path>/', methods = ['GET', 'POST'])
def page(path):
    """
    Access page from path
    """    
    page = pages.get_or_404(path)
    content = Content.from_page(page)
    form = None
    # enable comments for posts only
    if content.content_type == 'posts' :
        form = CommentForm()
    # form management
    if form and form.validate_on_submit() :
        author = form.name.data
        content = form.content.data
        page.add_comment(author, content)
    return render('page.html', page = content, form = form)


@app.route('/category/<category>')
def category(category) :
    """
    Filter posts by category
    """
    posts = [p for p in g.posts if p.category == category]
    # pagination
    try :
        page = int(request.args.get('page', 1))
    except ValueError :
        page = 1
    per_page = app.config[u'PAGINATION']    
    pagination = create_pagination(page, per_page, posts)
    # get content for current page
    displayed = get_objects_for_page(posts, page, per_page)
    return render('index.html', title = category, pages = displayed,
            pagination = pagination)


@app.route('/tag/<tag>')
def tag(tag) :
    """
    Filter posts by tag
    """
    posts = [p for p in g.posts if tag in p.tags.split(',')]
    # pagination
    try :
        page = int(request.args.get('page', 1))
    except ValueError :
        page = 1
    per_page = app.config[u'PAGINATION']    
    pagination = create_pagination(page, per_page, posts)
    # get content for current page
    displayed = get_objects_for_page(posts, page, per_page)
    return render('index.html', title = tag, pages = displayed,
            pagination = pagination)


@app.route('/archives')
def archives() :
    """
    Page listing all contents
    """
    # sort pages by reverse date
    sorted_pages = sorted(
                        [Content.from_page(p) for p in pages],
                        key = lambda x : x.published,
                        reverse = True
                    )
    # pagination
    try :
        page = int(request.args.get('page', 1))
    except ValueError :
        page = 1
    per_page = 10   
    pagination = create_pagination(page, per_page, sorted_pages)
    # get content for current page
    displayed = get_objects_for_page(sorted_pages, page, per_page)
    return render('archive.html',  pages = displayed, 
            pagination = pagination)


@app.route('/search/', methods = ['POST'])
def search() :
    """
    Search in contents
    """
    if not g.search_form.validate_on_submit() :
        return redirect(url_for('index'))
    query = g.search_form.search.data
    contents = search_query(query)
    # sort not draft contents by reverse date
    sorted_contents = sorted(
                            [c for c in contents if not c.draft], 
                            key = lambda x : x.published,
                            reverse = True
                       )
    # pagination
    try :
        page = int(request.args.get('page', 1))
    except ValueError :
        page = 1
    per_page = 20    
    pagination = create_pagination(page, per_page, sorted_contents)
    # get content for current page
    displayed = get_objects_for_page(sorted_contents, page, per_page)
    return render('index.html', title = query, pages = displayed,
            pagination = pagination)

    


@app.route('/feed.atom')
def feed() :
    """
    Generate feeds
    """
    if app.config.get('RSS', 'NO') != 'YES' :
        abort(404)
    name = app.config['SITENAME']
    feed = AtomFeed(name,feed_url=request.url, url=request.url_root)
    # sort posts by reverse date
    for post in g.posts[:20] :
        feed.add( post.meta.get(u'title'),
                unicode(post.summary),
                content_type = 'html',
                author = post.meta.get('author', ''),
                url = urljoin(request.url_root, post.path),
                updated = post.published)
    return feed.get_response()


@clize
def run_server(port = 8000, ip = '127.0.0.1') :
    """
    Run Microbe app on Cherrypy server

    port: Server socket port

    ip: Server socket host
    """
    import cherrypy
    from paste.translogger import TransLogger
    # enable paste logging
    app_logged = TransLogger(app)
    # mount the wsgi callable object on the root dir
    cherrypy.tree.graft(app_logged, '/')
    # set cherrypy config
    cherrypy.config.update({
        'engine.autoreload_on' : True,
        'log.screen' : True,
        'server.socket_port' : port,
        'server.socket_host' : ip
    })
    # start server
    cherrypy.engine.start()
    cherrypy.engine.block()


def main() :
    init_index()
    run(run_server)
