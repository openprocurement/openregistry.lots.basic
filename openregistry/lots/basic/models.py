# -*- coding: utf-8 -*-
from schematics.types import (
    StringType,
    MD5Type,
)
from schematics.types.compound import ListType
from zope.interface import implementer

from openregistry.lots.core.models import (
    ILot,
    Lot as BaseLot,
    validate_asset_uniq
)


class IBasicLot(ILot):
    """ Marker interface for basic lotss """


@implementer(IBasicLot)
class Lot(BaseLot):
    lotType = StringType(default="basic")
    lotIdentifier = StringType(required=True, min_length=1)
    assets = ListType(MD5Type(), required=True, min_size=1,
                      validators=[validate_asset_uniq])

    _internal_type = 'basic'
