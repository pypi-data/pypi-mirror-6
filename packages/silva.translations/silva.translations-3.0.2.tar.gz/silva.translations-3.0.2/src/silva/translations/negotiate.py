# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from infrae.wsgi.interfaces import IRequest
from zope.i18n.interfaces import IUserPreferredLanguages


def negotiate(request):
    """Monkey patch zope.i18n.negotiate not to rely on environment
    variable, and to cache its computation.
    """
    if IRequest.providedBy(request):
        if 'I18N_LANGUAGE' in request.other:
            return request.other['I18N_LANGUAGE']
        adapter = IUserPreferredLanguages(request)
        languages = adapter.getPreferredLanguages()
        if languages:
            language = languages[0]
        else:
            language = 'en'
        request.other['I18N_LANGUAGE'] = language
        return language
    return None
