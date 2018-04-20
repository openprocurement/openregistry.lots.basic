# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openregistry.lots.core.interfaces import IContentConfigurator, ILotManager
from openregistry.lots.basic.models import Lot, IBasicLot
from openregistry.lots.basic.adapters import BasicLotConfigurator, BasicLotManagerAdapter


def includeme(config):
    config.add_lotType(Lot)
    config.scan("openregistry.lots.basic.views")
    config.scan("openregistry.lots.basic.subscribers")
    config.registry.registerAdapter(BasicLotConfigurator,
                                    (IBasicLot, IRequest),
                                    IContentConfigurator)
    config.registry.registerAdapter(BasicLotManagerAdapter,
                                    (IBasicLot, ),
                                    ILotManager)
