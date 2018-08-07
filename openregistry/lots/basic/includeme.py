# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openregistry.lots.core.interfaces import IContentConfigurator, ILotManager
from openregistry.lots.basic.models import Lot, IBasicLot
from openregistry.lots.basic.adapters import BasicLotConfigurator, BasicLotManagerAdapter
from openregistry.lots.basic.constants import DEFAULT_LOT_TYPE


def includeme(config, plugin_config=None):
    config.scan("openregistry.lots.basic.views")
    config.scan("openregistry.lots.basic.subscribers")
    config.registry.registerAdapter(BasicLotConfigurator,
                                    (IBasicLot, IRequest),
                                    IContentConfigurator)
    config.registry.registerAdapter(BasicLotManagerAdapter,
                                    (IBasicLot, ),
                                    ILotManager)

    lot_types = plugin_config.get('aliases', [])
    if plugin_config.get('use_default', False):
        lot_types.append(DEFAULT_LOT_TYPE)
    for lt in lot_types:
        config.add_lotType(Lot, lt)

    # add accreditation level
    config.registry.accreditation['lot'][Lot._internal_type] = plugin_config['accreditation']
