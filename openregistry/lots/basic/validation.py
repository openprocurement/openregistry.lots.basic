# -*- coding: utf-8 -*-
from openregistry.lots.core.utils import raise_operation_error


def validate_document_operation_in_not_allowed_lot_status(request, error_handler, **kwargs):
    status = request.validated['lot_status']
    if status != 'pending':
        raise_operation_error(request, error_handler,
                              'Can\'t update document in current ({}) lot status'.format(status))
