# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openregistry.lots.basic.models import Lot, IBasicLot
from openregistry.lots.basic.adapters import BasicLotConfigurator


def includeme(config):
    config.add_lotType(Lot)
    config.scan("openregistry.lots.basic.views")
    config.scan("openregistry.lots.basic.subscribers")
    config.registry.registerAdapter(BasicLotConfigurator,
                                    (IBasicLot, IRequest),
                                    IContentConfigurator)
