# -*- coding: utf-8 -*-
from importlib import import_module
import os
from threading import RLock


__all__ = ['settings']


SETTINGS_ENV_NAME = "CHAMONIX_SETTINGS"
settings = None


class ConfigurationUnavailable(Exception): pass
class NoSuchSettings(Exception): pass


class LazySetting(object):

    user_settings_value = None
    user_settings_module = None

    def __init__(self):
        if LazySetting.user_settings_module is None:
            try:
                LazySetting.user_settings_value = os.environ[SETTINGS_ENV_NAME]
            except KeyError:
                raise ConfigurationUnavailable("%s not defined" % SETTINGS_ENV_NAME)
            LazySetting.user_settings_module = import_module(
                LazySetting.user_settings_value)

    def __getattribute__(self, name):
        """
        Override this unconditional attribute
        accessor method.
        """
        try:
            return getattr(LazySetting.user_settings_module, name)
        except AttributeError:
            raise NoSuchSettings("%s does not have settings named %s" % (
                LazySetting.user_settings_value, name))

def _initialize_settings_obj():
    global settings
    with RLock() as lock:
        if settings is None:
            settings = LazySetting()

_initialize_settings_obj()