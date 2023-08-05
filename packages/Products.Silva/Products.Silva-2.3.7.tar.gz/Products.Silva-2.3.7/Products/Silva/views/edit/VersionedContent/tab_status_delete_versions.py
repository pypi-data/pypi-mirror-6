## Script (Python) "tab_status_delete_versions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Revoke approval of approved content
##
from Products.Silva.i18n import translate as _
from Products.Silva.adapters.version_management import \
        getVersionManagementAdapter
from zope.i18n import translate

request = context.REQUEST
model = request.model
adapter = getVersionManagementAdapter(model)

if not request.has_key('versions'):
    return context.tab_status(message_type="error",
                            message=_("No versions selected"))

versions = request['versions']
if not same_type(versions, []):
    # request variable is not a list - probably just one checkbox
    # selected.
    versions = [versions,]

if len(versions) == len(adapter.getVersionIds()):
    return context.tab_status(message_type="error",
                                message=_("Can't delete all versions"))

result = adapter.deleteVersions(versions)

messages = []
for id, error in result:
    if error is not None:
        msg = _('could not delete ${id}: ${error}',
                mapping={'id': id, 'error': error})
        messages.append(translate(msg))
    else:
        msg = _('deleted ${id}',
                mapping={'id': id})
        messages.append('<span class="error">' + translate(msg) + '</span>')

return context.tab_status(message_type="feedback",
                        message=', '.join(messages).capitalize())
