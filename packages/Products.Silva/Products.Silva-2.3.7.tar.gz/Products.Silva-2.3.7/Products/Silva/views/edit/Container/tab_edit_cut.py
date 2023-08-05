## Script (Python) "tab_edit_cut"
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

if ids is None:
    return context.tab_edit(message_type="error", message=_("Nothing was selected, so nothing was cut."))

cut_ids = []
not_cut_ids = []
message_type = 'feedback'
for id in ids:
    if model.is_delete_allowed(id):
        cut_ids.append(id)
    else:
        not_cut_ids.append(id)

model.action_cut(ids, context.REQUEST)

if cut_ids:
    if not_cut_ids:
        message = _('Placed ${cut_ids} on clipboard for cutting, but could not cut ${not_cut_ids}.',
                    mapping={'cut_ids': context.quotify_list(cut_ids),
                             'not_cut_ids': context.quotify_list(not_cut_ids)
            })
    else:
        message = _('Placed ${cut_ids} on clipboard for cutting.',
                    mapping={'cut_ids': context.quotify_list(cut_ids)})
else:
    message = _('Could not place ${not_cut_ids} on clipboard for cutting.',
                mapping={'not_cut_ids': context.quotify_list(not_cut_ids)})
    message_type = 'error'

return context.tab_edit(message_type=message_type, message=message)
