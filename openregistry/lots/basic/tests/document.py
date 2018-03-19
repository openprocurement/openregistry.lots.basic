# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.blanks.mixins import ResourceDocumentTestMixin
from openregistry.lots.basic.tests.base import (
    LotContentWebTest
)
from openprocurement.api.tests.blanks.json_data import test_document_data
from openprocurement.api.constants import DOCUMENT_TYPES


class LotDocumentWithDSResourceTest(LotContentWebTest, ResourceDocumentTestMixin):
    docservice = True
    document_types = DOCUMENT_TYPES

    # status, in which operations with lot documents (adding, updating) are forbidden
    forbidden_document_modification_actions_status = 'active.salable'

    def setUp(self):
        super(LotDocumentWithDSResourceTest, self).setUp()
        self.initial_document_data = deepcopy(test_document_data)
        self.initial_document_data['url'] = self.generate_docservice_url()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LotDocumentWithDSResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
