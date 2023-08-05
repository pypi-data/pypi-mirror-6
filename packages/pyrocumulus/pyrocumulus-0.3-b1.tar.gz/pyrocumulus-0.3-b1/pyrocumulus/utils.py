#-*- coding: utf-8 -*-

from pyrocumulus.conf import settings


def get_value_from_settings(key, default=None):
    value = getattr(settings, key, default)
    return value
