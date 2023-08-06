# -*- coding: utf-8 -*-
import gettext
from gettext import gettext as _

import web

from chamonix.views.base import BaseView
from chamonix import utils
from chamonix.config import settings


__all__ = [
    "I18N",
    "Index"
]


class I18N(BaseView):

    # All translations, cached
    translations = web.storage()

    def pre_response(self, *args, **kwargs):
        lang = web.ctx.path.split('/')[1]
        self.lang = lang

    def load_translation(self):
        lang = getattr(self, 'lang', None)
        if lang not in settings.LANGS:
            raise web.notfound(self.render('notfound', msg=_("Un supported language")))
        else:
            translation = gettext.translation(
                'messages',
                settings.LOCALE_DIR,
                languages=[settings.LANGS[self.lang]],
            )
        return translation

    def get_translation(self):
        translation = self.translations.get(self.lang)
        if translation is None:
            translation = self.load_translation()
            self.translations[self.lang] = translation
        return translation

    def translate(self, string):
        translation = self.get_translation()
        if not translation:
            return unicode(string)
        return translation.ugettext(string)

    def render_i18n(self, tmpl, **kwargs):
        _globals = kwargs
        _globals.update({
            '_':self.translate,
            'lang': self.lang
        })
        return self.render(tmpl, _globals=_globals)

class Index(I18N):

    @utils.memoize
    def get(self, *args, **kwargs):
        return self.render_i18n('index')
