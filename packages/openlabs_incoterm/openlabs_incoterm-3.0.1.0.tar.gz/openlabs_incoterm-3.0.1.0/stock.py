# -*- coding: utf-8 -*-
"""

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from incoterm import Incoterm

__all__ = ['ShipmentOut', 'ShipmentOutIncoterm']
__metaclass__ = PoolMeta


class ShipmentOut:
    'Shipment Incoterm'
    __name__ = 'stock.shipment.out'

    incoterms = fields.One2Many(
        'stock.shipment.out.incoterm', 'shipment_out',
        'Stock Shipment Incoterm', states={
            'readonly': Eval('state') != 'draft',
        }, depends=['state'],
    )


class ShipmentOutIncoterm(Incoterm, ModelSQL, ModelView):
    'Shipment Out Incoterm'
    __name__ = 'stock.shipment.out.incoterm'

    shipment_out = fields.Many2One(
        'stock.shipment.out', 'Shipment Out', required=True
    )
