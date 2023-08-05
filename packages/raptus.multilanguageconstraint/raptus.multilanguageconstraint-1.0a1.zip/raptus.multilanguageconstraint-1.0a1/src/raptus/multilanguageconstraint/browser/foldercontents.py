import os

from Acquisition import aq_inner

from zope.i18n import translate

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.app.content.browser import foldercontents

from raptus.multilanguageconstraint import _


class FolderContentsView(foldercontents.FolderContentsView):
    __call__ = ViewPageTemplateFile(os.path.join(os.path.dirname(foldercontents.__file__), 'folder_contents.pt'))

    def contents_table(self):
        table = FolderContentsTable(aq_inner(self.context), self.request)
        return table.render()


class FolderContentsTable(foldercontents.FolderContentsTable):

    def __init__(self, context, request, contentFilter=None):
        if contentFilter is None:
            contentFilter = {}
        contentFilter['language_constraint'] = 'all'
        super(FolderContentsTable, self).__init__(context, request, contentFilter)

    def folderitems(self):
        return FolderContentsItems(self.context, self.request, super(FolderContentsTable, self).folderitems())


class FolderContentsItems(object):

    def __init__(self, context, request, items):
        self.context = context
        self.request = request
        self.catalog = getToolByName(context, 'portal_catalog')
        self.items = items

    def __iter__(self):
        for item in self.items:
            if (not 'not-available-in-language' in item['table_row_class'] and
                not len(self.catalog(UID=item['brain'].UID))):
                item['table_row_class'] += ' not-available-in-language'
                item['url_href_title'] += ' * %s' % translate(_(u'not available in this language'), context=self.request)
            yield item

    def __len__(self):
        return len(self.items)

    def __getslice__(self, i, j):
        return FolderContentsItems(self.context, self.request, self.items[i:j])

    def __add__(self, other):
        return FolderContentsItems(self.context, self.request, self.items + other.items)


class FolderContentsKSSView(foldercontents.FolderContentsKSSView):
    table = FolderContentsTable
