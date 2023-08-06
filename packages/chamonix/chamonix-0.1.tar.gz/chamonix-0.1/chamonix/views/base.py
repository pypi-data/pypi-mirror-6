# -*- coding: utf-8 -*-
import gettext
from gettext import gettext as _
from datetime import datetime

import web
from web import template

from chamonix.config import settings


__all__ = (
    'BaseView'
)

class TypeView(type):
    """
    Metaclass for all views.
    """

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, '_views'):
            setattr(cls, '_views', [])
        else:
            cls._views.append(cls)

class BaseView(object):

    __metaclass__ = TypeView

    def pre_response(self, *args, **kwargs):
        """
        Override this if any extra work need to be done.
        """
        pass

    def post_response(self, response):
        """
        Override this if any extra work need to be done.
        """
        pass

    def GET(self, *args, **kwargs):
        self.pre_response(*args, **kwargs)
        response = self.get(*args, **kwargs)
        self.post_response(response)
        return response

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def POST(self, *args, **kwargs):
        self.pre_response(*args, **kwargs)
        response = self.post(*args, **kwargs)
        self.post_response(response)
        return response

    def post(self, *args, **kwargs):
        raise NotImplementedError

    def render(self, tmpl, _globals=None, **kwargs):
        if _globals is None:
            _globals = {}
        _globals.update(kwargs)
        render = template.render(settings.TMPL_DIR, base=settings.TMPL_LAYOUT, globals=_globals)
        return getattr(render, tmpl)()
