# -*- coding: utf-8 -*-
from copy import deepcopy
from uuid import uuid4

from openprocurement.api.utils import get_now
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.tests.base import create_blacklist

from openregistry.lots.basic.models import Lot
from openregistry.lots.basic.constants import STATUS_CHANGES
from openregistry.lots.core.constants import LOT_STATUSES

ROLES = ['lot_owner', 'Administrator', 'concierge', 'convoy']
STATUS_BLACKLIST = create_blacklist(STATUS_CHANGES, LOT_STATUSES, ROLES)


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


def check_patch_status_200(self, path, lot_status, headers=None):
    response = self.app.patch_json(path,
                                   headers=headers,
                                   params={'data': {'status': lot_status}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], lot_status)


def check_patch_status_403(self, path, lot_status, headers=None):

    # Check if response.status is forbidden, when you try to change status to incorrect
    # 'data' should be {'data': {'status': allowed_status}}
    response = self.app.patch_json(path,
                                   params={'data': {'status': lot_status}},
                                   headers=headers,
                                   status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


def create_single_lot(self, data):
    response = self.app.post_json('/', {"data": data})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'draft')
    return response


def check_lotIdentifier(self):
    data = deepcopy(self.initial_data)
    data['lotIdentifier'] = ''
    response = self.app.post_json('/', {"data": data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'][0]['description'], ["String value is too short."])

    del data['lotIdentifier']
    response = self.app.post_json('/', {"data": data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'][0]['description'], ["This field is required."])

    data['lotIdentifier'] = 'Q24421K222'
    lot = create_single_lot(self, data).json['data']
    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(lot))
    self.assertEqual(response.json['data'], lot)


def check_lot_assets(self):

    # lot with a single assets
    self.initial_data["assets"] = [uuid4().hex]
    lot = create_single_lot(self, self.initial_data).json['data']
    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(lot))
    self.assertEqual(response.json['data'], lot)

    # lot with different assets
    self.initial_data["assets"] = [uuid4().hex, uuid4().hex]
    lot = create_single_lot(self, self.initial_data).json['data']
    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(lot))
    self.assertEqual(response.json['data'], lot)

    # # lot with no assets
    self.initial_data["assets"] = []
    response = self.app.post_json('/', {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Please provide at least 1 item."], u'location': u'body', u'name': u'assets'}
    ])
    # # lot with equal assets
    id_ex = uuid4().hex
    self.initial_data["assets"] = [id_ex, id_ex]
    response = self.app.post_json('/', {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Assets should be unique"], u'location': u'body', u'name': u'assets'}
    ])


def change_draft_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    # Create lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['assets'] = [uuid4().hex]
    response = create_single_lot(self, draft_lot)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'draft' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'draft', access_header)

    # Move from 'draft' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Create lot in draft status
    draft_lot = deepcopy(draft_lot)
    draft_lot['status'] = 'draft'
    lot = create_single_lot(self, draft_lot).json['data']

    # Move from 'draft' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['draft']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Create lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/', {'data': draft_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'draft' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['draft']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('convoy', ''))

    # Create lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/', {'data': draft_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'draft' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['draft']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Create lot in 'draft' status
    draft_lot = deepcopy(draft_lot)
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/', {'data': draft_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'draft' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['draft']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'draft' to 'draft' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'draft')

    # Move from 'draft' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')


def change_pending_lot(self):

    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)


    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = deepcopy(self.initial_data)
    lot_info['status'] = 'draft'

    # Create lot in 'draft' status and move it to 'pending'
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}

    response = self.app.get('/{}'.format(lot['id']), headers=access_header)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'deleted' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'deleted', access_header)

    # Create lot in 'draft' status and move it to 'pending'
    response = create_single_lot(self, deepcopy(lot_info))
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    lot = response.json['data']

    # Move from 'draft' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    # Create lot in 'draft' status and move it to 'pending'
    response = create_single_lot(self, deepcopy(lot_info))
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    lot = response.json['data']

    # Move from 'draft' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'pending' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'pending' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'pending' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')

    # Move from 'pending' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'pending' to 'deleted'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'deleted')


def change_verification_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)


    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move status from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move status from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    # Move from 'verification' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['verification']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'verification' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['verification']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move status from 'verification' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'pending' to 'verification' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'verification' to 'active.salable' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'pending' to 'verification' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'verification' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['verification']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move status from 'verification' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'pending' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')

    # Move from 'pending' to 'verification' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'active.salable' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'verification' status
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['verification']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


def change_deleted_lot(self):

    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)


    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'deleted'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'deleted', access_header)

    # Move from 'deleted' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['deleted']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'deleted' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['deleted']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'deleted' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['deleted']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'deleted' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['deleted']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


def change_pending_dissolution_lot(self):

    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)


    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    # Move status from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move status from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move status from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    self.app.authorization = ('Basic', ('broker', ''))

    # Move status from 'active.salable' to 'pending.dissolution'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.dissolution', access_header)

    # Move from 'pending.dissolution' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending.dissolution']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'pending.dissolution' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending.dissolution']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'pending.dissolution' to 'pending.dissolution'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.dissolution')

    # Move from 'pending.dissolution' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'pending.dissolution'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.dissolution')

    # Move from 'pending.dissolution' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending.dissolution']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'pending.dissolution' to 'dissolved'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'dissolved')


    self.app.authorization = ('Basic', ('broker', ''))

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move status from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')

    # Move status from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move status from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move status from 'active.salable' to 'pending.dissolution'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.dissolution')


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'pending.dissolution' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending.dissolution']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'pending.dissolution' to 'pending.dissolution'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.dissolution')

    # Move from 'pending.dissolution' to 'dissolved'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'dissolved')


def change_active_salable_lot(self):

    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)


    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.salable' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.salable']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)

    # Move from 'active.salable' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable', access_header)

    # Move from 'active.salable' to 'pending.dissolution'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.dissolution', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'pending.dissolution' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')


    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.salable' to 'recomposed'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'recomposed', access_header)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'recomposed' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable', access_header)



    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'active.salable' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.salable']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'active.salable' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.salable']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'active.salable' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'pending.dissolution'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.dissolution')

    # Move from 'pending.dissolution' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'recomposed'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'recomposed')

    # Move from 'recomposed' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')


    self.app.authorization = ('Basic', ('broker', ''))

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'active.salable' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.salable']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'active.salable' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable', access_header)

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')


def change_active_awaiting_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')


    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.awaiting' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.awaiting']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'active.awaiting' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.awaiting']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'active.awaiting' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.awaiting']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'active.awaiting' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'active.awaiting' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.awaiting']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'active.awaiting' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')


def change_active_auction_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.auction' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.auction']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'active.auction' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.auction']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'active.auction' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.auction']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'active.auction' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to 'sold'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.sold')

    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['active.auction']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'active.auction' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to 'sold'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.sold')


def change_dissolved_lot(self):

    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)


    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'pending.dissolution'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.dissolution')

    # Move from 'pending.dissolution' to 'dissolved'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'dissolved')

    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'dissolved' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['dissolved']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)

    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'dissolved' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['dissolved']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'dissolved' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['dissolved']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'dissolved' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['dissolved']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


def change_pending_sold_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to 'pending.sold'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.sold')


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'pending.sold' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending.sold']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'pending.sold' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending.sold']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)

    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'pending.sold' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending.sold']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'pending.sold' to 'sold'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'sold')


    self.app.authorization = ('Basic', ('broker', ''))

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to 'pending.sold'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.sold')

    # Move from 'pending.sold' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['pending.sold']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'pending.sold' to 'sold'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'sold')


def change_sold_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)

    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'active.awaiting'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.awaiting')

    # Move from 'active.awaiting' to 'active.auction'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.auction')

    # Move from 'active.auction' to 'pending.sold'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending.sold')

    # Move from 'pending.sold' to 'sold'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'sold')


    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'sold' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['sold']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'sold' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['sold']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'sold' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['sold']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'sold' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['sold']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


def change_recomposed_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    lot_info = self.initial_data
    lot_info['status'] = 'draft'

    # Create new lot in 'draft' status
    response = create_single_lot(self, lot_info)
    lot = response.json['data']
    token = response.json['access']['token']
    access_header = {'X-Access-Token': str(token)}
    self.assertEqual(lot['status'], 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending', access_header)

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification', access_header)


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')


    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.salable' to 'recomposed'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'recomposed', access_header)

    # Move from 'recomposed' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['recomposed']['lot_owner']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status, access_header)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'recomposed' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['recomposed']['concierge']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('convoy', ''))

    # Move from 'recomposed' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['recomposed']['convoy']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'recomposed' to 'recomposed'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'recomposed')

    # Move from 'recomposed' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')


    self.app.authorization = ('Basic', ('administrator', ''))

    # Move from 'pending' to 'verification'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'verification')

    # Move from 'verification' to 'active.salable'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'active.salable')

    # Move from 'active.salable' to 'recomposed'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'recomposed')

    # Move from 'recomposed' to one of 'blacklist' status
    for status in STATUS_BLACKLIST['recomposed']['Administrator']:
        check_patch_status_403(self, '/{}'.format(lot['id']), status)

    # Move from 'recomposed' to 'recomposed'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'recomposed')

    # Move from 'recomposed' to 'pending'
    check_patch_status_200(self, '/{}'.format(lot['id']), 'pending')
