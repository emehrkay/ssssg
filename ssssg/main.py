from typing import Any
import markdown
import os
import re
import pathlib

from datetime import datetime
from dateutil import parser

from .config import options

from tornado.web import template, _UIModuleNamespace, TemplateModule, _linkify, _xsrf_form_html
from tornado.template import ObjectDict

def log(content, error=False):
    ctrl = "\t" if error else ""
    print(ctrl, content)

def contents(file):
    """simply open a file"""
    with open(file) as f:
        return f.read()


def write(path, content):
    with open(path, 'w') as out:
        out.write(content)


def slugify(s):
    """
    Simplifies ugly strings into something URL-friendly.
    >>> print slugify("[Some] _ Article's Title--")
    some-articles-title

    @thanks: http://dolphm.com/slugify-a-string-in-python/
    """
    s = s.lower()

    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')

    s = re.sub('\W', '', s)
    s = s.replace('_', ' ')
    s = re.sub('\s+', ' ', s)
    s = s.strip()
    s = s.replace(' ', '-')

    return s


def slugify_path(path):
    parts = path.split(os.sep)
    parts = map(slugify, parts)

    return os.sep.join(parts)


class SSSG:

    def __init__(self, site_path, source_path=None, template_path=None,
                 output_path=None):
        site_path = os.path.expanduser(site_path if site_path else '')
        site_path = os.path.abspath(site_path)
        self.site_path = site_path
        self.source_path = source_path or os.path.join(site_path, 'src')
        self.template_path =  template_path or os.path.join(site_path,
            'template')
        self.output_path =  output_path or os.path.join(site_path,
            'public').rstrip(os.sep)
        self.tags_page = os.path.join(self.template_path, 'tags_page.html')
        self.tag_dir = f'{self.output_path}/_tags'
        self.site = site_path
        self.site_map = {}
        self.site_files = {}
        self.published_pages = {}
        self.template = Template(self.template_path)
        self.pages = Pages(source_path=source_path)
        self.tags = TaggedPages(page=self.tags_page, template=self.template)

    def create_site(self):
        # build the site map. The load the actual files, and finally save the
        # files. This is done in muliple steps so that when a page
        # is processed, it will able able to receive a list of its siblings
        self.build_pages()
        self.pages.sort()
        log((f'found {len(self.pages)} files that'
            ' will be used to create the site'))

    def save(self):
        """will save the published pages"""
        for page in self.pages.get_published_pages():
            site_path = page.path_to_page.replace('.md', '').replace(
                self.source_path, '').strip('/')
            save_path = self.output_path

            # ensure we are not creating a directory for the index file that
            # that lives at the source_path
            if page.full_path() != f'{self.source_path}{os.sep}index.md':
                site_path = slugify_path(site_path)
                save_path = os.path.join('', self.output_path, site_path)

                try:
                    os.makedirs(save_path, exist_ok=True)
                except Exception as e:
                    log((f'unable to create directories: {save_path}'
                        f' because: {e}'), True)
                    continue

            try:
                save_file = os.path.join(save_path, 'index.html')
                log(f'saving {save_file}')

                published = self.pages.get_published_pages()
                prev_page = self.pages.get_previous_page(page)
                next_page = self.pages.get_next_page(page)
                content = page.render(published_pages=published,
                    previous_page=prev_page, next_page=next_page)
                write(save_file, content)
            except Exception as e:
                log(f'unable to save file: {save_file} -- {e}', True)

        unpublished = self.pages.get_unpublished_pages()
        if len(unpublished):
            log('')
            log('these pages were unpublished and not rendered:', True)
            for up in unpublished:
                log(up.path_to_page, True)
            log('')

        # build the _tags pages
        for tag, pages in self.tags.pages.items():
            content = self.tags.render(tag, pages)
            tag_index_dir = f'{self.tag_dir}/{slugify(tag)}'
            tag_index = f'{tag_index_dir}/index.html'
            os.makedirs(tag_index_dir, exist_ok=True)
            write(tag_index, content)

        log('finished builidng site')

    def build_pages(self):
        for root, _, files in os.walk(self.source_path):
            for file in files:
                full_path = os.path.join(root, file)

                if file.endswith('.md'):
                    page = MarkdownPage(template=self.template,
                        source_path=self.source_path, path_to_page=full_path,
                        tag_dir=self.tag_dir)
                else:
                    continue

                self.pages.add_page(page)

                if not page.published:
                    continue

                for tag in page.tags():
                    self.tags[tag.tag] = page

    def index_directories(self):
        pass

    def directory_index(paths):
        pass


class Template:

    def __init__(self, template_path):
        self.template_path = template_path
        self.loader = template.Loader(self.template_path)
        self._active_modules = {}

    def render_string(self, string, **template_kwargs):
        temp = template.Template(string, loader=self.loader)
        return temp.generate(**template_kwargs)

    def render_file(self, file_path, **template_kwargs):
        file_bytes = contents(file_path)
        temp = template.Template(file_bytes, autoescape=None,
            loader=self.loader)
        return temp.generate(**template_kwargs)

    def _ui_module(self, name, module):
        def render(*args, **kwargs) -> str:  # type: ignore
            if not hasattr(self, "_active_modules"):
                self._active_modules = {}
            if name not in self._active_modules:
                self._active_modules[name] = module(self)
            rendered = self._active_modules[name].render(*args, **kwargs)
            return rendered

        return render


class Pages:

    def __init__(self, source_path, pages=None):
        self.source_path = source_path
        self.pages = pages or []

    def add_page(self, page):
        self.pages.append(page)

    def sort(self):
        """sorts the pages by published date descending"""
        self.pages.sort(key=lambda p: p.published_date, reverse=True)

        return self

    def get_published_pages(self):
        return [p for p in self.pages if p.published]

    def get_unpublished_pages(self):
        return [p for p in self.pages if not p.published]

    def get_previous_page(self, page):
        return None

    def get_next_page(self, page):
        return None

    def __len__(self):
        return len(self.pages)


class Page:

    def __init__(self, template, source_path, tag_dir, content=None):
        self.template = template
        self.tag_dir = tag_dir
        self.source_path = source_path
        self.content = content
        self.published = True
        self.published_date = None or datetime.now()
        self.title = None
        self.meta = {}

    def render(self, published_pages=None, previous_page=None, next_page=None):
        return self.content

    def path(self):
        return self.source_path

    def full_path(self):
        return self.source_path


class TaggedPages:

    def __init__(self, page, template):
        self.path_to_page = page
        self.template = template
        self.pages = {}

    def __setitem__(self, tag, page) -> None:
        if tag not in self.pages:
            self.pages[tag] = []

        self.pages[tag].append(page)

    def render(self, tag, published_pages=None):
        published_pages = published_pages or []
        template_kwargs = {
            'tag': tag,
            'pages': published_pages,
        }

        return self.template.render_file(self.path_to_page,
            **template_kwargs).decode('utf-8')


class Tag:

    def __init__(self, tag, tag_dir='/_tags'):
        self.tag = tag
        self.slug = slugify(tag)
        self.path = f'{tag_dir}/{self.slug}'



class MarkdownPage(Page):

    def __init__(self, template, source_path, tag_dir, path_to_page=None,
                 extensions=None):
        super().__init__(template=template, source_path=source_path, tag_dir=tag_dir)
        self.path_to_page = path_to_page
        _, self.page_name = os.path.split(self.path_to_page)
        extensions = extensions or ['markdown.extensions.meta', 'codehilite']
        self.md = markdown.Markdown(extensions=extensions)
        self.build()

    def build(self):
        try:
            self.content = self.md.convert(contents(self.path_to_page))

            try:
                self.meta = self.md.Meta
            except Exception as e:
                self.meta = {}

            try:
                published = self.md.Meta['published'][0].lower()
                self.published = published in ['true', '1', 1]
            except Exception as e:
                self.published = False

            if not self.published:
                return ''

            # figure out the published date for the article
            # first, try to use the published_date from meta
            # if that doesnt work, use the file creation date
            # if that doesnt work, use now
            try:
                self.published_date = self.meta['published_date'][0]
                self.published_date = parser.parse(self.published_date)
            except Exception as e:
                try:
                    stat = pathlib.Path(self.path_to_page)
                    self.published_date = datetime.fromtimestamp(
                        stat.stat().st_mtime)
                except Exception as e:
                    self.published_date = datetime.now()

            # get the title
            # first, attempt to get it from the meta data
            # if that doesnt work, use the file name with title casing
            try:
                self.title = self.meta.get('title')[0]
            except:
                self.title = self.page_name.replace('.md', '').title()

        except Exception as e:
            log((f'something went wrong while transforming the file'
                ' {page_name} locatated at: {path} into markdown -- {e}'),
                True)

    def path(self):
        path = self.path_to_page.replace('.md', '').replace(self.source_path, '')

        return slugify_path(path)

    def full_path(self):
        return self.path_to_page

    def tags(self):
        final = []
        tag_list = self.meta.get('tags', [''])

        for tags in tag_list:
            for tag in tags.split(','):
                tag = tag.strip()

                if tag != '':
                    final.append(Tag(tag))

        return final

    def render(self, published_pages=None, previous_page=None, next_page=None):
        published_pages = published_pages or []
        template_kwargs = {
            'meta': self.meta,
            'title': self.title,
            'pages': published_pages,
            'previous_page': previous_page,
            'next_page': next_page,
            'published_date': self.published_date,
        }

        return self.template.render_string(self.content,
            **template_kwargs).decode('utf-8')
