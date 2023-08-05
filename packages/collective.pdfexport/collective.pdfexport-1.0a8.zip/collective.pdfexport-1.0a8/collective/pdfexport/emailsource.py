from collective.pdfexport.interfaces import IPDFEmailSource
from five import grok
from zope.interface import Interface
from plone.memoize import ram
from time import time
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from plone import api

class DefaultEmailSource(grok.Adapter):
    grok.context(Interface)
    grok.implements(IPDFEmailSource)
    grok.name('userid')

    def __init__(self, context):
        self.context = context

    @ram.cache(lambda *args: 'UserSource%s' % (time() // (60 * 60)))
    def options(self):
        vocab = getUtility(
            IVocabularyFactory,
            name='plone.principalsource.Users'
        )(self.context)
        values = set()
        for i in vocab:
            user = api.user.get(i.value)
            if not user:
                continue
            fullname = user.getProperty('fullname')
            email = user.getProperty('email')
            if not email:
                continue
            value = '%s <%s>' % (fullname, email)
            values.add((i.value, fullname))
        return [
            {'value': 'UserID:%s' % v, 'title': t} for v, t in values
        ]

    def can_expand(self, value):
        return value.startswith('UserID:')

    def expand_value(self, value):
        username = value.replace('UserID:','')
        user = api.user.get(username)
        if not user:
            return []
        fullname = user.getProperty('fullname')
        email = user.getProperty('email')
        if not email:
            return []
        value = '%s <%s>' % (fullname, email)
        return [value]

    def search(self, query):
        options = self.options()
        return [
            v for v in options if query.lower() in v['title'].lower()
        ]






class GroupEmailSource(grok.Adapter):
    grok.context(Interface)
    grok.implements(IPDFEmailSource)
    grok.name('groupid')

    @ram.cache(lambda *args: 'GroupSource%s' % (time() // (60 * 60)))
    def options(self):
        values = ['Group:%s' % g.id for g in api.group.get_groups()]
        return [
            {'value': v, 'title': v} for v in values
        ]

    def search(self, query):
        options = self.options()
        return [
            v for v in options if query.lower() in v['title'].lower()
        ]

    def can_expand(self, value):
        return value.startswith('Group:')

    def expand_value(self, value):
        values = []
        groupid = value.replace('Group:', '')
        users = api.user.get_users(groupname=groupid)
        for user in users:
            values.append('%s <%s>' % (
                user.getProperty('fullname'),
                user.getProperty('email')
            ))
        return list(set(values))
