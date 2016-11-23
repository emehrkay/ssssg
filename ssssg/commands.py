import copy
import json
import os
import re
import sys
import uuid

from pathlib import Path

import markdown

from tornado import ioloop
from tornado.web import Application

from . import options
from . import SSSSGException


def run_ssssg(site, *args):
    """
    """
    from . import IndexHandler, PageHandler, ErrorHandler, options

    options.parse_command_line(args)

    site_cache_file = cache_file(site)

    if not Path(site_cache_file):
        raise SSSSGException(('There is no cache file for site: {} in'
            ' location: {}'.format(site, site_cache_file)))

    cache = json.loads(contents(site_cache_file))
    routes = (
        (r'/', IndexHandler),
        (r'/([\w\_\-]+)/?', PageHandler),
    )

    if 'config_file' in cache:
        options.parse_config_file(cache['config_file'])

    options.parse_command_line(args)

    settings = {
        'debug': options.debug,
        'site_cache_file': site_cache_file,
        'static_path': cache['site']['static_path'],
        'autoescape': None,
        'default_handler_class': ErrorHandler,
        #'ui_modules': cache['site']['ui_modules'],
    }

    app = Application(routes, **settings)
    app.cache = cache

    app.listen(options.port)

    print('{} is running on port: {}'.format(site, options.port))

    ioloop.IOLoop.current().start()


def build_index(site, *args):
    site = os.path.abspath(site)
    site_name = list(filter(bool, site.split(os.sep)))[-1]
    index = {
        'site': {
            'name': site_name,
            'path': site,
            'ui_modules' : os.path.join(site, 'modules'),
            'static_path': os.path.join(site, 'static'),
            'template_path': os.path.join(site, 'templates'),
        },
        'pages': {},
    }
    index_md = os.path.join(site, 'index.md')
    config_file = os.path.join(site, 'config.py')

    if os.path.isfile(config_file):
        index['config_file'] = config_file
        options.parse_config_file(config_file)

    options.parse_command_line(args)

    index_file = cache_file(site_name)

    def make_slug(parts):
        if not parts:
            parts = [str(uuid.uuid4())]

        parts = list(filter(bool, parts))
        slug = '-'.join(parts).lower()

        return re.sub('\W', '-', slug)

    for root, subdirs, files in os.walk(site):
        parts = root.replace(site, '').split(os.sep)

        for f in files:
            if f.endswith('.md'):
                md = markdown.Markdown(
                    extensions=['markdown.extensions.meta'])
                _file = os.path.join(root, f)
                md.convert(contents(_file))

                try:
                    meta = md.Meta
                except Exception as e:
                    meta = {}

                try:
                    title = meta.get('title')[0]
                except:
                    title = f.replace('.md', '')

                try:
                    slug = meta.get('slug')[0]
                except:
                    sp = parts[:]
                    sp.append(title)
                    slug = make_slug(sp)

                try:
                    tags = map(str.strip, meta.get('tags')[0].split(','))
                except:
                    tags = []

                try:
                    published = meta.get('published')[0].strip().lower()

                    if published not in ['true', 'false']:
                        published = bool(published)

                    published = bool(json.loads(published))
                except:
                    published = True

                try:
                    templates = meta.get('templates')[0].split(',')
                except:
                    templates = []

                if _file == index_md:
                    slug = '/'

                try:
                    date_published = meta.get('date_published')[0]
                except Exception as e:
                    date_published = os.path.getmtime(_file)

                index['pages'][slug] = {
                    'tags': list(tags),
                    'title': title,
                    'file': _file,
                    'published': published,
                    'templates': templates,
                    'date_created': os.path.getctime(_file),
                    'date_modified': os.path.getmtime(_file),
                    'date_published': date_published,
                }

    os.makedirs(os.path.dirname(index_file), exist_ok=True)

    with open(index_file, 'w') as f:
        f.write(json.dumps(index))

    return index


def contents(file):
    with open(file) as f:
        return f.read()


def cache_file(site_name):
    return os.path.join(options.cache_file_directory,
        '{}.cache'.format(site_name))


def filter_by_tags(tags, cache):
    if not isinstance(tags, (list, tuple)):
        tags = [tags,]

    pages = {}

    for slug, page in cache.items():
        if page['published'] and set(tags) & set(page['tags']):
            pages[slug] = page

    return pages
