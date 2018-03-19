# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from uuid import uuid4

from openregistry.lots.core.tests.base import (
    BaseLotWebTest as BaseLWT
)
from openprocurement.api.tests.blanks.json_data import test_lot_data


class BaseLotWebTest(BaseLWT):
    initial_auth = ('Basic', ('broker', ''))
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        self.initial_data = deepcopy(test_lot_data)
        self.initial_data['assets'] = [uuid4().hex]
        super(BaseLotWebTest, self).setUp()


class LotContentWebTest(BaseLotWebTest):
    init = True
    initial_status = 'pending'
