from urllib import urlencode

from Products.CMFCore.utils import getToolByName

from zope.publisher.browser import BrowserView
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class NotAvailableView(BrowserView):
    """ View displayed if content is not available in the
        visitors' language
    """

    def __init__(self, context, request):
        super(NotAvailableView, self).__init__(context, request)
        self.vocabulary = getUtility(IVocabularyFactory, 'plone.app.vocabularies.SupportedContentLanguages')(self.context)
        self.languageTool = getToolByName(self.context, 'portal_languages')
        self.language = self.vocabulary.getTerm(self.languageTool.getPreferredLanguage()).title

    def available_languages(self):
        available_languages = []
        field = self.context.Schema()['language_constraint']
        binding = self.request.get('LANGUAGE_TOOL', None)
        if binding is None:
            self.languageTool.setLanguageBindings()
            binding = self.request.get('LANGUAGE_TOOL')
        language = binding.LANGUAGE
        url = self.context.absolute_url() + '/switchLanguage?'
        for lang in field.get(self.context):
            binding.LANGUAGE = lang
            available_languages.append({
                'language': self.vocabulary.getTerm(lang).title,
                'title': self.context.Title(),
                'description': self.context.Description(),
                'url': url + urlencode({
                    'set_language': lang
                })
            })
        binding.LANGUAGE = language
        return available_languages

    def __call__(self):
        self.request.response.setStatus(404)
        return self.index()
