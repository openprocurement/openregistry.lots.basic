# -*- coding: utf-8 -*-
from openregistry.lots.core.adapters import LotConfigurator, LotManagerAdapter
from openregistry.lots.core.validation import (
    validate_post_lot_role,

)
from .constants import STATUS_CHANGES


class BasicLotConfigurator(LotConfigurator):
    """ BelowThreshold Tender configuration adapter """

    name = "Basic Lot configurator"
    available_statuses = STATUS_CHANGES


class BasicLotManagerAdapter(LotManagerAdapter):
    name = 'Basic Lot Manager'
    create_validation = (
        validate_post_lot_role,
    )
    def create_lot(self, request):
        self._validate(request, self.create_validation)

    def change_lot(self, request):
        pass
