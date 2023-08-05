from Acquisition import aq_parent
from AccessControl import getSecurityManager

from zope import interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions


class IMultilanguageConstraintView(interface.Interface):
    """ Help view to add / remove languages
    """

    def add(languages, include_children=False):
        """ Adds the specified languages optionally also to
            all childrens
        """

    def remove(languages, include_children=False):
        """ Removes the specified languages optionally also from
            all childrens
        """


class MultilanguageConstraintView(BrowserView):
    """ Help view to add / remove languages
    """
    interface.implements(IMultilanguageConstraintView)

    def __init__(self, context, request):
        super(MultilanguageConstraintView, self).__init__(context, request)
        self.plone_utils = getToolByName(context, 'plone_utils')
        self.catalog = getToolByName(context, 'portal_catalog')

    def update(self, obj, action, languages):
        if not getSecurityManager().checkPermission(permissions.ModifyPortalContent, obj):
            return
        field = obj.Schema()['language_constraint']
        current = list(field.get(obj))
        available = field.get(aq_parent(obj))
        languages = [lang for lang in languages if (lang in available and
                                                    ((action == 'add' and not lang in current) or
                                                     (action == 'remove' and lang in current)))]
        if languages:
            if action == 'add':
                new_languages = current + languages
            else:
                new_languages = [lang for lang in current if not lang in languages]
            field.set(obj, new_languages)
            obj.reindexObject(['language_constraint'])

    def add(self, languages, include_children=False):
        """ Adds the specified languages optionally also to
            all childrens
        """
        if include_children:
            for child in self.catalog(path='/'.join(self.context.getPhysicalPath()),
                                      sort_on='path',
                                      unfiltered=True):
                self.update(child.getObject(), 'add', languages)
        else:
            self.update(self.context, 'add', languages)

    def remove(self, languages, include_children=False):
        """ Removes the specified languages optionally also from
            all childrens
        """
        self.update(self.context, 'remove', languages)
