from plone.indexer.decorator import indexer

from Products.ATContentTypes.interfaces.interfaces import IATContentType


@indexer(IATContentType)
def language_constraint(object, **kw):
    return object.Schema()['language_constraint'].get(object)
