from Acquisition import aq_parent

from zope.interface import implementer
from zope.component import getUtility
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory

from Products.ATContentTypes.interfaces.interfaces import IATContentType


@implementer(IVocabularyFactory)
def languages_vocabulary_factory(context):
    parent = aq_parent(context)
    if IATContentType.providedBy(parent):
        selected = parent.Schema()['language_constraint'].get(parent)
        languages = languages_vocabulary_factory(parent)
        filtered = []
        for term in languages:
            if not term.value in selected:
                continue
            filtered.append(term)
        return vocabulary.SimpleVocabulary(filtered)
    return getUtility(IVocabularyFactory, 'plone.app.vocabularies.SupportedContentLanguages')(parent)
