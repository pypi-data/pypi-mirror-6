## Script (Python) "tab_edit_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None
##title=
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
deleted_ids = []
not_deleted_ids = []
message_type = 'feedback'

if ids is None:
    return context.tab_edit(message_type="error", message=_("Nothing was selected, so nothing was deleted."))

for id in ids:
    if model.is_delete_allowed(id):
        deleted_ids.append(id)
    else:
        not_deleted_ids.append(id)

model.action_delete(ids)

if deleted_ids:
    if not_deleted_ids:
        message = _("Deleted ${deleted_ids}, but could not delete "
                    "${not_deleted_ids}. Probably there is a published "
                    "version that must be closed, or an approved version that "
                    "needs to be revoked. Change the status in the Publish "
                    "screen (alt-5).",
                    mapping={'deleted_ids': context.quotify_list(deleted_ids),
                             'not_deleted_ids':
                             context.quotify_list(not_deleted_ids)
                             })
    else:
        message = _('Deleted ${deleted_ids}.',
                    mapping={'deleted_ids': context.quotify_list(deleted_ids)})
    model.sec_update_last_author_info()
else:
    message = _('Could not delete ${not_deleted_ids}. Possibly there is a published version, which must be closed before it can be deleted. Or, the document is approved (the link will be green), and approval needs to be revoked. Change the status in the Publish screen (alt-5).',
                mapping={'not_deleted_ids': context.quotify_list(not_deleted_ids)})
    message_type = 'error'

return context.tab_edit(message_type=message_type, message=message)
