from tornado.web import Application, RequestHandler, template

import markdown

from .config import options
from .commands import contents


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
        md = markdown.Markdown(extensions=['markdown.extensions.meta'])

        if not slug or slug not in self.application.cache:
            page = options.four_oh_four
        else:
            page = self.application.cache[slug]['file']

        page = self.get_page(page)
        content = self._template_string(page)

        return self.write(content)


class IndexHandler(PageHandler):

    def get(self):
        return super().get('/')
