# -*- coding: utf-8 -*-
import web

from chamonix.config import settings


def create_db():
    # TODO (Chaobin Tang) Pool connection for re-use
    conn = web.database(**settings.DB)
    return conn
