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
        raise_operation_error(
            request,
            error_handler,
            'Can\'t update lot in current ({}) status'.format(current_status)
        )


def validate_lot_status_update_in_terminated_status_for_admin(request, error_handler, **kwargs):

    current_status = request.context.status
    new_status = validate_json_data(request).get('status')
    lot = request.context
    request.validated['data'] = {'status': new_status}
    if request.authenticated_role == 'Administrator' and current_status in ['deleted', 'dissolved', 'sold']:
        raise_operation_error(request, error_handler, 'Can\'t update lot in current ({}) status'.format(lot.status))
