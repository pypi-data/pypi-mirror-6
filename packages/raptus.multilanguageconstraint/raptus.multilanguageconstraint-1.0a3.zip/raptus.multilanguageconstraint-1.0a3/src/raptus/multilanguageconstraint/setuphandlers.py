from Products.CMFCore.utils import getToolByName


def install(context):
    if context.readDataFile('raptus.multilanguageconstraint_install.txt') is None:
        return
    portal = context.getSite()

    catalog = getToolByName(portal, 'portal_catalog')
    if not 'language_constraint' in catalog.indexes():
        catalog.addIndex('language_constraint', 'KeywordIndex')
        catalog.reindexIndex('language_constraint', portal.REQUEST)
