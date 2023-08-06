# -*- coding: utf-8 -*-
"""

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval
from incoterm import Incoterm

__all__ = ['Sale', 'SaleIncoterm']
__metaclass__ = PoolMeta


class Sale:
    'Sale'
    __name__ = 'sale.sale'

    incoterms = fields.One2Many(
        'sale.incoterm', 'sale', 'Sales Incoterm', states={
            'readonly': Eval('state') != 'draft',
        }, depends=['state', 'currency', 'total_amount'],
        context={
            'currency': Eval('currency'),
            'value': Eval('total_amount'),
        }
    )

    def create_invoice(self, invoice_type):
        '''
        Create and return an invoice of type invoice_type
        '''
        InvoiceIncoterm = Pool().get('account.invoice.incoterm')

        invoice = super(Sale, self).create_invoice(invoice_type)

        if invoice:
            InvoiceIncoterm.create(map(
                lambda incoterm: {
                    'year': incoterm.year,
                    'abbrevation': incoterm.abbrevation,
                    'value': incoterm.value,
                    'currency': incoterm.currency.id,
                    'city': incoterm.city,
                    'invoice': invoice.id,
                }, self.incoterms
            ))

        return invoice

    def create_shipment(self, shipment_type):
        '''
        Create and return shipments of type shipment_type
        '''
        ShipmentIncoterm = Pool().get('stock.shipment.out.incoterm')

        shipments = super(Sale, self).create_shipment(shipment_type)

        if shipment_type != 'out':
            return shipments

        for shipment in shipments:
            ShipmentIncoterm.create(map(
                lambda incoterm: {
                    'year': incoterm.year,
                    'abbrevation': incoterm.abbrevation,
                    'value': incoterm.value,
                    'currency': incoterm.currency.id,
                    'city': incoterm.city,
                    'shipment_out': shipment.id,
                }, self.incoterms
            ))

        return shipments


class SaleIncoterm(Incoterm, ModelSQL, ModelView):
    'Sale Incoterm'
    __name__ = 'sale.incoterm'

    sale = fields.Many2One('sale.sale', 'Sale', required=True)
