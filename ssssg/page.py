import copy

from tornado.web import Application, RequestHandler, template

import markdown

from .config import options
from .commands import contents, filter_by_tags


class PageHandler(RequestHandler):

    def _template_string(self, string, **kwargs):
        temp = template.Template(string, autoescape=None)
        args = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
            options=options,
        )
        args.update(**kwargs)
        args.update(self.ui)

        return temp.generate(**args)

    def get_page(self, page):
        md = markdown.Markdown(extensions=['markdown.extensions.meta'])

        return md.convert(contents(page))

    def get(self, slug=None):
        try:
            tags = self.get_argument('tags', None).split(',')
        except:
            tags = None

        md = markdown.Markdown(extensions=['markdown.extensions.meta'])
        cache = self.application.cache['pages']
        data = {}

        if not slug or slug not in cache:
            page = options.four_oh_four
        elif tags:
            page = options.search_template
            data['pages'] = filter_by_tags(tags, cache)
            data['tags'] = tags
            data['content'] = self.render_string(page, **data)
        else:
            p_slug = cache[slug]
            page = p_slug['file']
            data = {
                'title': p_slug['title'],
            }

            converted = md.convert(contents(page))
            data['content'] = self._template_string(converted)

        content = self.render_string(options.base_template, **data)

        return self.finish(content)


class IndexHandler(PageHandler):

    def get(self):
        return super().get('/')
