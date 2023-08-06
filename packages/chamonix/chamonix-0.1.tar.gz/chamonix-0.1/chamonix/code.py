# -*- coding: utf-8 -*-
import os

import web

from chamonix import view, config


urls = config.URLS

def application():
    app = web.application(urls, globals())
    return app

app = application()

if __name__ == '__main__':
    app.run()