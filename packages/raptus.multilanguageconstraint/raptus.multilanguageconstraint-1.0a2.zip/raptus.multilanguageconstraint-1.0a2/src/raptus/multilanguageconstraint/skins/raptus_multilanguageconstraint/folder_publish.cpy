## Controller Python Script "folder_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, paths=[], comment='No comment', expiration_date=None, effective_date=None, include_children=False, language_action=None, languages=None
##title=Publish objects from a folder
##

from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as p

plone_utils=context.plone_utils
REQUEST=context.REQUEST

if workflow_action is None and language_action is None:
    context.plone_utils.addPortalMessage(p(u'You must select a publishing action.'), 'error')
    return state.set(status='failure')
if not paths:
    context.plone_utils.addPortalMessage(p(u'You must select content to change.'), 'error')
    return state.set(status='failure')

if workflow_action is not None:
    failed = plone_utils.transitionObjectsByPaths(workflow_action, paths, comment,
                                                  expiration_date, effective_date,
                                                  include_children, REQUEST=REQUEST)

    transaction_note( str(paths) + ' transitioned ' + workflow_action )

    context.plone_utils.addPortalMessage(p(u'Item state changed.'))

# Add/Remove selected languages
if languages and language_action in ('remove', 'add'):
    portal = context.portal_url.getPortalObject()
    traverse = portal.restrictedTraverse
    catalog = portal.portal_catalog
    for path in paths:
        o = traverse(path, None)
        if o is None:
            continue
        view = o.restrictedTraverse('@@multilanguageconstraint')
        getattr(view, language_action)(languages, include_children)

# It is necessary to set the context to override context from content_status_modify
return state.set(context=context)
