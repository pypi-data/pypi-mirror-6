#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

from five import grok
from collective import dexteritytextindexer
from plone.dexterity.interfaces import IDexterityContent

class MySearchableTextExtender(grok.Adapter):
    grok.context(IDexterityContent)
    grok.name('MCIPublication')
    grok.implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        """Extend the searchable text with a custom string"""
        ret = []
        content = [
            getattr(self.context, 'title', ''),
            getattr(self.context, 'description', ''),
            getattr(self.context, 'subject', ''),]
        if getattr(self.context, 'portal_type', '') in ['publication']:
            content.extend([
                getattr(self.context, 'dcterm_issue', ''),]) 
        for i in content:
            if isinstance(i, (list, tuple)):
                i = ' '.join(i)
            if isinstance(i, basestring):
                i = i.strip()
            if i and (not i in ret):
                ret.append(i)
        ret = ' '.join(ret)
        return ret


