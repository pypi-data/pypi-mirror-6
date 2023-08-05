## Controller Python Script "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##

from Products.CMFPlone import transaction_note
ids = context.REQUEST.get('ids', [])
titles = []
titles_and_ids = []

status = 'failure'
message = 'No vocabulary to delete.'

for id in ids:
    obj = context.restrictedTraverse(id)
    titles.append(obj.title_or_id())
    titles_and_ids.append('%s (%s)' % (obj.title_or_id(), obj.getId()))

if ids:
    status = 'success'
    message = ', '.join(titles)+' has been deleted.'
    transaction_note('Deleted %s from %s' % (', '.join(titles_and_ids), context.absolute_url()))
    context.manage_delObjects(ids)

qs = context.create_query_string(portal_status_message=message)

return context.REQUEST.RESPONSE.redirect('%s/view?%s' % (context.absolute_url(), qs))
