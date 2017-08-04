# -*- coding: utf-8 -*-
from copy import deepcopy
from uuid import uuid4

from openregistry.api.utils import get_now
from openregistry.api.constants import ROUTE_PREFIX

from openregistry.lots.basic.models import Lot


# LotTest

def simple_add_lot(self):
    u = Lot(self.initial_data)
    u.lotID = "UA-X"
    u.assets = [uuid4().hex]

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.lotID == fromdb['lotID']
    assert u.doc_type == "Lot"

    u.delete_instance(self.db)


def listing(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    lots = []

    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json('/lots', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lots.append(response.json['data'])

    ids = ','.join([i['id'] for i in lots])

    while True:
        response = self.app.get('/lots')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in lots]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in lots]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in lots]))

    while True:
        response = self.app.get('/lots?offset={}'.format(offset))
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/lots?limit=2')
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('prev_page', response.json)
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.get('/lots', params=[('opt_fields', 'status')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
    self.assertIn('opt_fields=status', response.json['next_page']['uri'])

    response = self.app.get('/lots?descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in lots]))
    self.assertEqual([i['dateModified'] for i in response.json['data']],
                     sorted([i['dateModified'] for i in lots], reverse=True))

    response = self.app.get('/lots?descending=1&limit=2')
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 0)

    test_lot_data2 = self.initial_data.copy()
    test_lot_data2['mode'] = 'test'
    response = self.app.post_json('/lots', {'data': test_lot_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    while True:
        response = self.app.get('/lots?mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/lots?mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)


def listing_changes(self):
    response = self.app.get('/lots?feed=changes')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    lots = []

    for i in range(3):
        response = self.app.post_json('/lots', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lots.append(response.json['data'])

    ids = ','.join([i['id'] for i in lots])

    while True:
        response = self.app.get('/lots?feed=changes')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(','.join([i['id'] for i in response.json['data']]), ids)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in lots]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in lots]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in lots]))

    response = self.app.get('/lots?feed=changes&limit=2')
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('prev_page', response.json)
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.get('/lots?feed=changes', params=[('opt_fields', 'status')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified', u'status']))
    self.assertIn('opt_fields=status', response.json['next_page']['uri'])

    response = self.app.get('/lots?feed=changes&descending=1')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in lots]))
    self.assertEqual([i['dateModified'] for i in response.json['data']],
                     sorted([i['dateModified'] for i in lots], reverse=True))

    response = self.app.get('/lots?feed=changes&descending=1&limit=2')
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get(response.json['next_page']['path'].replace(ROUTE_PREFIX, ''))
    self.assertEqual(response.status, '200 OK')
    self.assertNotIn('descending=1', response.json['prev_page']['uri'])
    self.assertEqual(len(response.json['data']), 0)

    test_lot_data2 = self.initial_data.copy()
    test_lot_data2['mode'] = 'test'
    response = self.app.post_json('/lots', {'data': test_lot_data2})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    while True:
        response = self.app.get('/lots?feed=changes&mode=test')
        self.assertEqual(response.status, '200 OK')
        if len(response.json['data']) == 1:
            break
    self.assertEqual(len(response.json['data']), 1)

    response = self.app.get('/lots?feed=changes&mode=_all_')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 4)


def listing_draft(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    lots = []
    data = self.initial_data.copy()
    data.update({'status': 'draft'})

    for i in range(3):
        response = self.app.post_json('/lots', {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lots.append(response.json['data'])
        response = self.app.post_json('/lots', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

    ids = ','.join([i['id'] for i in lots])

    while True:
        response = self.app.get('/lots')
        self.assertTrue(ids.startswith(','.join([i['id'] for i in response.json['data']])))
        if len(response.json['data']) == 3:
            break

    self.assertEqual(len(response.json['data']), 3)
    self.assertEqual(set(response.json['data'][0]), set([u'id', u'dateModified']))
    self.assertEqual(set([i['id'] for i in response.json['data']]), set([i['id'] for i in lots]))
    self.assertEqual(set([i['dateModified'] for i in response.json['data']]), set([i['dateModified'] for i in lots]))
    self.assertEqual([i['dateModified'] for i in response.json['data']], sorted([i['dateModified'] for i in lots]))


def create_lot(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/lots', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(lot))
    self.assertEqual(response.json['data'], lot)

    response = self.app.post_json('/lots?opt_jsonp=callback', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"', response.body)

    response = self.app.post_json('/lots?opt_pretty=1', {"data": self.initial_data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json('/lots', {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "', response.body)


def check_lot_assets(self):


    def create_single_lot():
        response = self.app.post_json('/lots', {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        return response.json['data']


    # lot with a single assets
    self.initial_data["assets"] = [uuid4().hex]
    lot = create_single_lot()
    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(lot))
    self.assertEqual(response.json['data'], lot)

    # lot with different assets
    self.initial_data["assets"] = [uuid4().hex, uuid4().hex]
    lot = create_single_lot()
    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(lot))
    self.assertEqual(response.json['data'], lot)

    # # this tests are not working corectly

    # # lot with no assets
    # self.initial_data["assets"] = []
    # response = self.app.post_json('/lots', {"data": self.initial_data})

    # # lot with equal assets
    # id_ex = uuid4().hex
    # self.initial_data["assets"] = [id_ex, id_ex]
    # response = self.app.post_json('/lots', {"data": self.initial_data})

    ####################################################################
    # TODO: fix the problem with no-assets-lot and different-assets-lot#
    # - they should return 403 or something, not raise erorrs.         #
    ####################################################################


def get_lot(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/lots', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    response = self.app.get('/lots/{}?opt_jsonp=callback'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get('/lots/{}?opt_pretty=1'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "data": {\n        "', response.body)


def patch_lot(self):
    data = self.initial_data.copy()
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/lots', {'data': data})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    owner_token = response.json['access']['token']
    dateModified = lot.pop('dateModified')

    response = self.app.patch_json('/lots/{}?acc_token={}'.format(
        lot['id'], owner_token), {'data': {'title': ' PATCHED'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']['dateModified'], dateModified)


def dateModified_lot(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.post_json('/lots', {'data': self.initial_data})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    dateModified = lot['dateModified']

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['dateModified'], dateModified)

    response = self.app.patch_json('/lots/{}?acc_token={}'.format(
        lot['id'], token), {'data': {'description': 'PATCHED'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.assertNotEqual(response.json['data']['dateModified'], dateModified)
    asset = response.json['data']
    dateModified = asset['dateModified']

    response = self.app.get('/lots/{}'.format(asset['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], asset)
    self.assertEqual(response.json['data']['dateModified'], dateModified)


def change_draft_lot(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    # Create lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/lots', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'deleted' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'deleted'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'deleted' to 'draft' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'draft'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Create new lot in 'draft' status
    draft_lot = deepcopy(draft_lot)
    draft_lot['assets'] = [uuid4().hex]
    response = self.app.post_json('/lots', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    # Move from 'draft' to 'waiting' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'waiting'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    # Move from 'waiting' to 'draft'
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'draft'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    self.app.authorization = ('Basic', ('bot1', ''))

    # Create lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/lots', {'data': draft_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move last 'draft' lot to 'deleted' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'deleted'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'draft' to 'waiting' status
    # XXX TODO Waiting to Waiting
    # response = self.app.patch_json(
    #     '/lots/{}?acc_token={}'.format(lot['id'], token),
    #     {'data': {'status': 'waiting'}},
    #     status=403,
    # )
    # self.assertEqual(response.status, '403 Forbidden')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')


def change_waiting_lot(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)


    self.app.authorization = ('Basic', ('bot1', ''))

    # Create new lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['assets'] = [uuid4().hex]
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/lots', {'data': draft_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    self.app.authorization = ('Basic', ('broker', ''))

    # Create new lot in 'draft' status
    response = self.app.post_json('/lots', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'waiting' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'waiting'}}
    )
    self.assertEqual(response.status, '200 OK')


    self.app.authorization = ('Basic', ('bot1', ''))

    # Move from 'waiting' to 'invalid' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'invalid'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'invalid' to 'waiting' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'waiting'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'invalid' to 'active.pending' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.pending'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    self.app.authorization = ('Basic', ('broker', ''))

    # Create new lot in 'draft' status
    response = self.app.post_json('/lots', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'waiting' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'waiting'}}
    )
    self.assertEqual(response.status, '200 OK')


    self.app.authorization = ('Basic', ('bot1', ''))

    # Move from 'waiting' to 'active.pending' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.pending'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'active.pending' to 'waiting' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'waiting'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'active.pending' to 'sold' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'sold'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    self.app.authorization = ('Basic', ('broker', ''))

    # Create new lot in 'waiting' status
    waiting_lot = deepcopy(self.initial_data)
    waiting_lot['status'] = 'waiting'
    waiting_lot['assets'] = [uuid4().hex]
    response = self.app.post_json('/lots', {'data': waiting_lot})
    self.assertEqual(response.status, '201 Created')
    token = response.json['access']['token']
    lot = response.json['data']

    # Move from 'waiting' to 'invalid' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'invalid'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'waiting' to 'active.pending' status
    response = self.app.patch_json(
        '/lots/{}'.format(lot['id']),
        {'data': {'status': 'active.pending'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'waiting' to 'sold' status
    response = self.app.patch_json(
        '/lots/{}'.format(lot['id']),
        {'data': {'status': 'sold'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


def change_dissolved_lot(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    # Create lot in 'active.pending' status
    pending_lot = deepcopy(self.initial_data)
    pending_lot['status'] = 'active.pending'
    response = self.app.post_json('/lots', {'data': pending_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Create new lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['assets'] = [uuid4().hex]
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/lots', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'waiting' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'waiting'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'waiting' to 'active.pending' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.pending'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    self.app.authorization = ('Basic', ('bot1', ''))
    # Move from 'waiting' to 'active.pending' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.pending'}}
    )
    self.assertEqual(response.status, '200 OK')


    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.pending' to 'dissolved' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'dissolved'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'dissolved' to 'active.pending' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.pending'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'dissolved' to 'invalid' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'invalid'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'dissolved' to 'deleted' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'deleted'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'dissolved' to 'sold' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'sold'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    # Create new lot in 'draft' status for bot
    draft_lot = deepcopy(self.initial_data)
    draft_lot['assets'] = [uuid4().hex]
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/lots', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'waiting' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'waiting'}}
    )
    self.assertEqual(response.status, '200 OK')


    self.app.authorization = ('Basic', ('bot1', ''))

    # Create lot in 'active.pending' status
    pending_lot = deepcopy(self.initial_data)
    pending_lot['status'] = 'active.pending'
    response = self.app.post_json('/lots', {'data': pending_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'waiting' to 'active.pending' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.pending'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'active.pending' to 'dissolved' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'dissolved'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.pending' to 'dissolved' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'dissolved'}}
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('bot1', ''))

    # Move from 'dissolved' to 'deleted' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'deleted'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'dissolved' to 'sold' status
    response = self.app.patch_json(
        '/lots/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'sold'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


def lot_not_found(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    response = self.app.get('/lots/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'lot_id'}
    ])

    response = self.app.patch_json(
        '/lots/some_id', {'data': {}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'lot_id'}
    ])

    # put custom document object into database to check asset construction on non-Asset data
    data = {'contract': 'test', '_id': uuid4().hex}
    self.db.save(data)

    response = self.app.get('/lots/{}'.format(data['_id']), status=404)
    self.assertEqual(response.status, '404 Not Found')


def change_lot_statuses_bot2(self):
    response = self.app.get('/lots')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('bot2', ''))

    inauction_lot = deepcopy(self.initial_data)
    inauction_lot['status'] = 'active.inauction'
    response = self.app.post_json('/lots', {'data': inauction_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']

    self.assertEqual(lot.get('status', ''), 'active.inauction')

    response = self.app.get('/lots/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    response = self.app.patch_json(
        '/lots/{}'.format(lot['id']),
        {'data': {'status': 'active.pending'}}
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/lots/{}'.format(lot['id']),
        {'data': {'status': 'active.inauction'}}
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/lots/{}'.format(lot['id']),
        {'data': {'status': 'sold'}}
    )
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/lots/{}'.format(lot['id']),
        {'data': {'status': 'active.inauction'}}
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
