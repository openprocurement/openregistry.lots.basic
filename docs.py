# -*- coding: utf-8 -*-
from openprocurement.api.tests.base import PrefixedRequestClass, DumpsTestAppwebtest
from openregistry.lots.basic.tests.base import BaseLotWebTest


class LotResourceTest(BaseLotWebTest):

    def setUp(self):
        super(LotResourceTest, self).setUp()
        self.app = DumpsTestAppwebtest(
            "config:tests.ini", relative_to=self.relative_to)
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def test_docs_tutorial(self):
        request_path = '/?opt_pretty=1'

        # Exploring basic rules
        #
        with open('docs/source/tutorial/lot-listing.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with open('docs/source/tutorial/lot-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        with open('docs/source/tutorial/lot-post-attempt-json.http', 'w') as self.app.file_obj:
            response = self.app.post(
                request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        # Creating lot in draft status
        #
        with open('docs/source/tutorial/lot-post-2pc.http', 'w') as self.app.file_obj:
            response = self.app.post_json(request_path, {"data": self.initial_data})
            self.assertEqual(response.status, '201 Created')

        lot_id = response.json['data']['id']
        owner_token = response.json['access']['token']

        with open('docs/source/tutorial/blank-lot-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/{}'.format(lot_id))
            self.assertEqual(response.status, '200 OK')

        # Switch to 'pending'
        #
        with open('docs/source/tutorial/lot-patch-2pc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                           {'data': {"status": 'pending'}})
            self.assertEqual(response.status, '200 OK')

        # Modifying lot
        #
        with open('docs/source/tutorial/patch-lot.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token), {'data':
                {
                    "description": "Змінений опис тестового лоту"
                }
            })
            self.assertEqual(response.status, '200 OK')

        self.app.get(request_path)
        with open('docs/source/tutorial/lot-listing-after-patch.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        # Switch to 'verification'
        #
        with open('docs/source/tutorial/lot-patch-2pc-verification.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                           {'data': {"status": 'verification'}})
            self.assertEqual(response.status, '200 OK')

        # Hack for update_after
        #
        self.app.get(request_path)
        #

        with open('docs/source/tutorial/initial-lot-listing.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/create-second-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(request_path, {"data": self.initial_data})
            self.assertEqual(response.status, '201 Created')

        second_lot_id = response.json['data']['id']
        second_owner_token = response.json['access']['token']

        with open('docs/source/tutorial/pending-second-lot.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}?acc_token={}'.format(second_lot_id, second_owner_token),
                                           {'data': {"status": 'pending'}})
            self.assertEqual(response.status, '200 OK')

        # Hack for update_after
        #
        self.app.get(request_path)
        #

        with open('docs/source/tutorial/listing-with-some-lots.http', 'w') as self.app.file_obj:
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        # Switch to 'deleted'
        #
        with open('docs/source/tutorial/lot-delete-2pc.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}?acc_token={}'.format(second_lot_id, second_owner_token),
                                           {'data': {"status": 'deleted'}})
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

    def test_docs_tutorial_with_concierge(self):
        request_path = '/?opt_pretty=1'

        response = self.app.post_json(request_path, {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')

        lot_id = response.json['data']['id']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                       {'data': {"status": 'pending'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                       {'data': {"status": 'verification'}})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('concierge', ''))

        # Switch to 'active.salable'
        #

        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'active.salable'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/concierge-patched-lot-to-active.salable.http', 'w') as self.app.file_obj:
            response = self.app.get('/{}'.format(lot_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Switch to 'pending.dissolution'
        #
        with open('docs/source/tutorial/patch-lot-to-pending.dissolution.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                           {'data': {"status": 'pending.dissolution'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'pending.dissolution')

        self.app.authorization = ('Basic', ('concierge', ''))

        # Switch to 'dissolved'
        #
        with open('docs/source/tutorial/patch-lot-to-dissolved.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}'.format(lot_id),
                                           {'data': {"status": 'dissolved'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'dissolved')

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(request_path, {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')

        lot_id = response.json['data']['id']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                       {'data': {"status": 'pending'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                       {'data': {"status": 'verification'}})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('concierge', ''))

        # Switch to 'pending' from 'verification'
        #
        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'pending'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/concierge-patched-lot-to-pending.http', 'w') as self.app.file_obj:
            response = self.app.get('/{}'.format(lot_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                       {'data': {"status": 'verification'}})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('concierge', ''))

        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'active.salable'}})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('convoy', ''))

        # Switch to 'active.awaiting'
        #
        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'active.awaiting'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/convoy-patched-lot-to-active.awaiting.http', 'w') as self.app.file_obj:
            response = self.app.get('/{}'.format(lot_id))
            self.assertEqual(response.status, '200 OK')

        # Switch to 'active.salable' from 'active.awaiting'
        #
        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'active.salable'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/convoy-patched-lot-to-active.salable.http', 'w') as self.app.file_obj:
            response = self.app.get('/{}'.format(lot_id))
            self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'active.awaiting'}})
        self.assertEqual(response.status, '200 OK')

        # Switch to 'active.auction'
        #
        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'active.auction'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/convoy-patched-lot-to-active.auction.http', 'w') as self.app.file_obj:
            response = self.app.get('/{}'.format(lot_id))
            self.assertEqual(response.status, '200 OK')

        # Switch to 'pending.sold'
        #
        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'pending.sold'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/convoy-patched-lot-to-pending.sold.http', 'w') as self.app.file_obj:
            response = self.app.get('/{}'.format(lot_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('concierge', ''))

        # Switch to 'sold'
        #
        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'sold'}})
        self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/patch-lot-to-sold-from-pending.sold.http', 'w') as self.app.file_obj:
            response = self.app.get('/{}'.format(lot_id))
            self.assertEqual(response.status, '200 OK')

        # Recomposed tutorial

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(request_path, {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')

        lot_id = response.json['data']['id']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                       {'data': {"status": 'pending'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                       {'data': {"status": 'verification'}})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('concierge', ''))

        # Switch to 'active.salable'
        #

        response = self.app.patch_json('/{}'.format(lot_id),
                                       {'data': {"status": 'active.salable'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/{}'.format(lot_id))
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        # Switch to 'recomposed'
        #
        with open('docs/source/tutorial/patch-lot-to-recomposed.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}?acc_token={}'.format(lot_id, owner_token),
                                           {'data': {"status": 'recomposed'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'recomposed')

        self.app.authorization = ('Basic', ('concierge', ''))

        # Switch to 'pending'
        #
        with open('docs/source/tutorial/patch-lot-to-pending-from-recomposed.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/{}'.format(lot_id),
                                           {'data': {"status": 'pending'}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'pending')
