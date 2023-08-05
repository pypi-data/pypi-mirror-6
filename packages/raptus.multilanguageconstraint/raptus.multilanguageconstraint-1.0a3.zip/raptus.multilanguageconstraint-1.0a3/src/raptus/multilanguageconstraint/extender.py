from zope.interface import implements
from zope.component import adapts, getUtility
from zope.schema.interfaces import IVocabularyFactory

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.ATContentTypes.interface import IATContentType

from raptus.multilanguageconstraint import _


class LanguagesField(atapi.LinesField):
    """ Languages field updating all childs
    """

    def set(self, instance, value, **kwargs):
        if not kwargs.get('_initializing_', False):
            removed = [lang for lang in self.get(instance) if not lang in value]
            if removed:
                catalog = getToolByName(instance, 'portal_catalog')
                for child in catalog(path={'query': '/'.join(instance.getPhysicalPath()) + '/'}, language_constraint=removed):
                    child = child.getObject()
                    super(LanguagesField, self).set(child, [lang for lang in self.get(child) if not lang in removed])
                    child.reindexObject(['language_constraint'])
        super(LanguagesField, self).set(instance, value, **kwargs)


class ExtensionLanguagesField(ExtensionField, LanguagesField):
    """ Language selection field
    """


class LanguageExtender(object):
    adapts(IATContentType)
    implements(ISchemaExtender)

    field = ExtensionLanguagesField(
        name = 'language_constraint',
        enforceVocabulary = True,
        vocabulary_factory = 'raptus.multilanguageconstraint.languages',
        storage = atapi.AnnotationStorage(),
        schemata = 'settings',
        widget=atapi.MultiSelectionWidget(
            label = _(u'label_languages', default=u'Languages'),
            description = _(u'description_languages', default=u'The languages this object is available in.'),
            format='checkbox',
        ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        vocabulary = getUtility(IVocabularyFactory, 'raptus.multilanguageconstraint.languages')(self.context)
        if not len(vocabulary):
            return []
        field = self.field.copy()
        field.default = [term.token for term in vocabulary]
        return [field]
