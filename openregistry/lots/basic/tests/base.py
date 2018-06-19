# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from uuid import uuid4

from openregistry.lots.core.tests.base import (
    BaseLotWebTest as BaseLWT
)
from openregistry.lots.core.tests.blanks.json_data import test_lot_data

from openregistry.lots.basic.tests.fixtures import PARTIAL_MOCK_CONFIG
from openregistry.lots.core.tests.base import (
    connection_mock_config,
    BaseWebTest as CoreWebTest,
    MOCK_CONFIG as BASE_MOCK_CONFIG
)


MOCK_CONFIG = connection_mock_config(PARTIAL_MOCK_CONFIG,
                                     base=BASE_MOCK_CONFIG,
                                     connector=('plugins', 'api', 'plugins',
                                                'lots.core', 'plugins'))

class BaseWebTest(CoreWebTest):
    mock_config = MOCK_CONFIG


class BaseLotWebTest(BaseLWT):
    initial_auth = ('Basic', ('broker', ''))
    relative_to = os.path.dirname(__file__)
    mock_config = MOCK_CONFIG

    def setUp(self):
        self.initial_data = deepcopy(test_lot_data)
        self.initial_data['assets'] = [uuid4().hex]
        super(BaseLotWebTest, self).setUp()


class LotContentWebTest(BaseLotWebTest):
    init = True
    initial_status = 'pending'
    mock_config = MOCK_CONFIG
