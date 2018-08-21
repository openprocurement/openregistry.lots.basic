# -*- coding: utf-8 -*-

STATUS_CHANGES = {
    "draft": {
        "editing_permissions": ["lot_owner", "Administrator"],
        "next_status": {
            "pending": ["lot_owner", "Administrator"],
        }
    },
    "pending": {
        "editing_permissions": ["lot_owner", "Administrator"],
        "next_status": {
            "pending.deleted": ["lot_owner", "Administrator"],
            "verification": ["lot_owner", "Administrator"]
        }
    },
    "pending.deleted": {
        "editing_permissions": ["concierge", "Administrator"],
        "next_status": {
            "deleted": ["concierge", "Administrator"],
        }
    },
    "deleted": {
        "editing_permissions": [],
        "next_status": {}
    },
    "verification": {
        "editing_permissions": ["concierge", "Administrator"],
        "next_status": {
            "pending": ["concierge", "Administrator"],
            "active.salable": ["concierge", "Administrator"]
        }
    },
    "recomposed": {
        "editing_permissions": ["concierge", "Administrator"],
        "next_status": {
            "pending": ["concierge", "Administrator"],
        }
    },
    "active.salable": {
        "editing_permissions": ["convoy", "Administrator", "lot_owner"],
        "next_status": {
            "pending.dissolution": ["lot_owner", "Administrator"],
            "recomposed": ["lot_owner", "Administrator"],
            "active.awaiting": ["convoy", "Administrator"],
            "verification": ["Administrator"]
        }
    },
    "pending.dissolution": {
        "editing_permissions": ["concierge", "Administrator"],
        "next_status": {
            "dissolved": ["concierge", "Administrator"],
            "active.salable": ["Administrator"]
        }
    },
    "dissolved": {
        "editing_permissions": [],
        "next_status": {}
    },
    "active.awaiting": {
        "editing_permissions": ["convoy", "Administrator"],
        "next_status": {
            "active.auction": ["convoy", "Administrator"],
            "active.salable": ["convoy", "Administrator"]
        }
    },
    "active.auction": {
        "editing_permissions": ["convoy", "Administrator"],
        "next_status": {
            "active.salable": ["convoy", "Administrator"],
            "pending.sold": ["convoy", "Administrator"]
        }
    },
    "pending.sold": {
        "editing_permissions": ['concierge',  'Administrator'],
        "next_status": {
            'sold': ['concierge',  'Administrator']
        }
    },
    "sold": {
        "editing_permissions": [],
        "next_status": {}
    }
}


DEFAULT_LOT_TYPE = 'basic'

DEFAULT_LEVEL_OF_ACCREDITATION = {'create': [1],
                                  'edit': [2]}
