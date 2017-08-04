# -*- coding: utf-8 -*-
import os
import unittest

from openregistry.api.tests.base import BaseWebTest, snitch

from openregistry.lots.basic.tests.base import (
    test_lot_data, BaseLotWebTest
)
from openregistry.lots.basic.tests.lot_blanks import (
    listing,
    get_lot,
    lot_not_found,
    dateModified_lot,
    listing_draft,
    listing_changes,
    create_lot,
    patch_lot,
    simple_add_lot,
    check_lot_assets,
)


class LotTest(BaseWebTest):
    initial_data = test_lot_data
    relative_to = os.path.dirname(__file__)
    test_simple_add_lot = snitch(simple_add_lot)


class LotResourceTest(BaseLotWebTest):
    initial_data = test_lot_data
    initial_auth = ('Basic', ('broker', ''))
    relative_to = os.path.dirname(__file__)
    test_create_lot = snitch(create_lot)
    test_patch_lot = snitch(patch_lot)
    test_lot_not_found = snitch(lot_not_found)
    test_listing = snitch(listing)
    test_get_lot = snitch(get_lot)
    test_dateModified_lot = snitch(dateModified_lot)
    test_listing_draft = snitch(listing_draft)
    test_listing_changes = snitch(listing_changes)
    test_check_lot_assets = snitch(check_lot_assets)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LotResourceTest))
    suite.addTest(unittest.makeSuite(LotTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
