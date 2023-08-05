# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.publisher.browser import BrowserLanguages


class SilvaLanguages(BrowserLanguages):
    """The first prefered language is the one set by the cookie.
    """

    def getPreferredLanguages(self):
        languages = super(SilvaLanguages, self).getPreferredLanguages()
        cookie_language = self.request.cookies.get('silva_language')
        if cookie_language is not None:
            languages = [cookie_language] + languages
        return languages
