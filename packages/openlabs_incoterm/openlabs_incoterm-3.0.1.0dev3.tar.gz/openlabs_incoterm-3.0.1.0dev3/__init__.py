# -*- coding: utf-8 -*-
"""
    __init__


    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from sale import Sale, SaleIncoterm
from stock import ShipmentOut, ShipmentOutIncoterm
from invoice import Invoice, InvoiceIncoterm


def register():
    Pool.register(
        Sale,
        SaleIncoterm,
        ShipmentOut,
        ShipmentOutIncoterm,
        Invoice,
        InvoiceIncoterm,
        module='incoterm', type_='model'
    )
