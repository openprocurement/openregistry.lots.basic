# -*- coding: utf-8 -*-
import os
import unittest

from openregistry.lots.basic.tests.base import BaseWebTest
from openregistry.lots.core.tests.base import snitch
from openregistry.lots.core.tests.blanks.mixins import (
    ResourceTestMixin,
    ExtractCredentialsMixin
)
from openregistry.lots.basic.tests.base import (
    test_lot_data, BaseLotWebTest
)

from openregistry.lots.basic.tests.base import (
    LotContentWebTest
)
from openregistry.lots.basic.tests.lot_blanks import (
    # LotResourceTest
    change_draft_lot,
    change_dissolved_lot,
    check_lot_assets,
    check_lotIdentifier,
    change_pending_lot,
    change_verification_lot,
    change_deleted_lot,
    change_pending_dissolution_lot,
    change_active_salable_lot,
    change_active_awaiting_lot,
    change_active_auction_lot,
    change_sold_lot,
    change_pending_sold_lot,
    change_recomposed_lot,
    change_pending_deleted_lot,
    # LotTest
    simple_add_lot
)


class LotTest(BaseWebTest):
    initial_data = test_lot_data
    relative_to = os.path.dirname(__file__)
    test_simple_add_lot = snitch(simple_add_lot)


class LotResourceTest(BaseLotWebTest, ResourceTestMixin):
    initial_status = 'pending'

    test_08_change_draft_lot = snitch(change_draft_lot)
    test_09_change_pending_lot = snitch(change_pending_lot)
    test_10_check_verification_lot = snitch(change_verification_lot)
    test_11_check_deleted_lot = snitch(change_deleted_lot)
    test_12_check_pending_dissolution_lot = snitch(change_pending_dissolution_lot)
    test_13_check_active_salable_lot = snitch(change_active_salable_lot)
    test_14_check_active_awaiting_lot = snitch(change_active_awaiting_lot)
    test_15_check_active_auction_lot = snitch(change_active_auction_lot)
    test_16_change_dissolved_lot = snitch(change_dissolved_lot)
    test_17_check_sold_lot = snitch(change_sold_lot)
    test_18_check_lot_assets = snitch(check_lot_assets)
    test_19_check_lot_lotIdentifier = snitch(check_lotIdentifier)
    test_20_check_pending_sold_lot = snitch(change_pending_sold_lot)
    test_21_check_recomposed_lot = snitch(change_recomposed_lot)
    test_22_change_pending_deleted_lot = snitch(change_pending_deleted_lot)


class LotExtractCredentialsTest(LotContentWebTest, ExtractCredentialsMixin):
    pass


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(LotResourceTest))
    tests.addTest(unittest.makeSuite(LotTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
