# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from openregistry.lots.core.events import LotInitializeEvent
from openregistry.lots.core.utils import get_now


@subscriber(LotInitializeEvent, lotType="basic")
def tender_init_handler(event):
    """ initialization handler for basic lots """
    event.lot.date = get_now()
