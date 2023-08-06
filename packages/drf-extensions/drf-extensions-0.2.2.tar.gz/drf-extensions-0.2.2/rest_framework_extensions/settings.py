# -*- coding: utf-8 -*-
from django.conf import settings

from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, 'REST_FRAMEWORK_EXTENSIONS', None)

DEFAULTS = {
    # caching
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': None,
    'DEFAULT_CACHE_KEY_FUNC': 'rest_framework_extensions.utils.default_cache_key_func',
    'DEFAULT_OBJECT_CACHE_KEY_FUNC': 'rest_framework_extensions.utils.default_object_cache_key_func',
    'DEFAULT_LIST_CACHE_KEY_FUNC': 'rest_framework_extensions.utils.default_list_cache_key_func',

    # ETAG
    'DEFAULT_ETAG_FUNC': 'rest_framework_extensions.utils.default_etag_func',
    'DEFAULT_OBJECT_ETAG_FUNC': 'rest_framework_extensions.utils.default_object_etag_func',
    'DEFAULT_LIST_ETAG_FUNC': 'rest_framework_extensions.utils.default_list_etag_func',

    # other
    'DEFAULT_KEY_CONSTRUCTOR_MEMOIZE_FOR_REQUEST': False
}

IMPORT_STRINGS = [
    'DEFAULT_CACHE_KEY_FUNC',
    'DEFAULT_OBJECT_CACHE_KEY_FUNC',
    'DEFAULT_LIST_CACHE_KEY_FUNC',
    'DEFAULT_ETAG_FUNC',
    'DEFAULT_OBJECT_ETAG_FUNC',
    'DEFAULT_LIST_ETAG_FUNC',
]


extensions_api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)