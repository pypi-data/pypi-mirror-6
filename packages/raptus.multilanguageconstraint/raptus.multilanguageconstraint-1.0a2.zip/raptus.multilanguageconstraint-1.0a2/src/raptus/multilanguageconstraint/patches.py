from Acquisition import aq_parent
from AccessControl import getSecurityManager

from zope.component import getMultiAdapter

from ZPublisher import BaseRequest
from Products.ZCatalog import ZCatalog
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import DynamicType, permissions
from Products.ATContentTypes.interfaces.interfaces import IATContentType


ZCatalog.ZCatalog.__old_searchResults = ZCatalog.ZCatalog.searchResults

def searchResults(self, REQUEST=None, used=None, unfiltered=False, **kw):
    """ Patched to reduce results by language availability
    """
    languageTool = getToolByName(self, 'portal_languages', None)
    if unfiltered or 'language_constraint' in kw:
        if 'language_constraint' in kw and kw['language_constraint'] == 'all':
            del kw['language_constraint']
        return self.__old_searchResults(**kw)
    kw['language_constraint'] = [languageTool.getPreferredLanguage()]
    return self.__old_searchResults(REQUEST, used, **kw)


BaseRequest.BaseRequest.__old_traverse = BaseRequest.BaseRequest.traverse

def traverse(self, path, response=None, validated_hook=None):
    object = self.__old_traverse(path, response, validated_hook)
    context = aq_parent(object)
    if (context is None or
        not IATContentType.providedBy(context) or
        getSecurityManager().checkPermission(permissions.ModifyPortalContent, context)):
        return object
    languageTool = getToolByName(context, 'portal_languages', None)
    if languageTool.getPreferredLanguage() in context.Schema()['language_constraint'].get(context):
        return object
    return getMultiAdapter((context, self), name='notavailable')
