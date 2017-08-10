# -*- coding: utf-8 -*-
from openregistry.api.validation import validate_json_data
from openregistry.api.utils import raise_operation_error

from openregistry.lots.basic.constants import STATUS_CHANGES


def validate_change_lot_status(request, error_handler, **kwargs):
    '''Validate status changes using STATUS_CHANGES rules.'''

    current_status = request.context.status
    new_status = validate_json_data(request).get('status')
    auth_role = request.authenticated_role

    if not new_status or auth_role == 'Administrator':
        return

    if new_status in STATUS_CHANGES[current_status] and \
       auth_role == STATUS_CHANGES[current_status][new_status]:
        request.validated['data'] = {'status': new_status}
    else:
        request.errors.add(
            'body', 'lot',
            'Can\'t update lot to ({}) status'.format(new_status)
        )
        request.errors.status = 403
        raise error_handler(request)
