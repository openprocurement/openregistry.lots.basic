# -*- coding: utf-8 -*-
from openregistry.lots.core.adapters import LotConfigurator, LotManagerAdapter

from .constants import STATUS_CHANGES


class BasicLotConfigurator(LotConfigurator):
    """ BelowThreshold Tender configuration adapter """

    name = "Basic Lot configurator"
    available_statuses = STATUS_CHANGES


class BasicLotManagerAdapter(LotManagerAdapter):
    name = 'Basic Lot Manager'

    def create_lot(self, request):
        pass