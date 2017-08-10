# -*- coding: utf-8 -*-
from openregistry.api.validation import validate_json_data
from openregistry.api.utils import raise_operation_error


def validate_document_operation_in_not_allowed_lot_status(request, error_handler, **kwargs):
    status = request.validated['lot_status']
    if status != 'pending':
        raise_operation_error(request, error_handler,
                              'Can\'t update document in current ({}) lot status'.format(status))


def validate_lot_empty_assets(request, error_handler, **kwargs):
    lot = validate_json_data(request)
    new_status = lot.get('status')
    assets = lot.get('assets')
    if assets == [] and new_status != 'draft':
        request.errors.add(
            'body', 'assets',
            'Empty assets allowed in draft status only'
        )
        request.errors.status = 422
        raise error_handler(request)
