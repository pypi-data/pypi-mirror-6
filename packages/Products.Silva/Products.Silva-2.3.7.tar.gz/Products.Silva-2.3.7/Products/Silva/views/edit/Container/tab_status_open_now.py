##parameters=refs=None
from Products.Silva.i18n import translate as _
request = context.REQUEST
model = request.model

if not refs:
  return context.tab_status(message_type='error', 
          message=_('Nothing was selected, so nothing was approved.'))

try:
    result = context.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return context.tab_status(
        message_type='error', 
        message=context.render_form_errors(e),
        refs=refs)

clear_expiration = result['clear_expiration']

objects = []
for ref in refs:
    obj = model.resolve_ref(ref)
    if obj:
        objects.append(obj)

message = context.open_now(objects, clear_expiration)
return context.tab_status(message_type='feedback', message=message)
