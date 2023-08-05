##parameters=refs=None
from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError

# Check whether there's any checkboxes checked at all...
if not refs:
    return context.tab_status(
        message_type='error',
        message=_('Nothing was selected, so no new version was created.'))

try:
    result = context.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return context.tab_status(
        message_type='error',
        message=context.render_form_errors(e),
        refs=refs)

copied_ids = []
not_copied = []
msg = []

objects = []
for ref in refs:
    obj = model.resolve_ref(ref)
    if obj:
        objects.append(obj)

def action(obj, fullPath, argv):
    if obj.get_next_version():
        return (False, (fullPath, _('already has a next version')))
    obj.create_copy()
    return (True, fullPath)

[copied_ids,not_copied,dummy] = context.do_publishing_action(objects,action=action)

if copied_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Created a new version for: ${ids}',
                mapping={'ids': context.quotify_list(copied_ids)})
    msg.append(translate(message))

if not_copied:
    message = _('could not create a new version for: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_copied)})
    msg.append('<span class="error">' + translate(message)  + '</span>')

return context.tab_status(message_type='feedback', message=(', '.join(msg)) )
