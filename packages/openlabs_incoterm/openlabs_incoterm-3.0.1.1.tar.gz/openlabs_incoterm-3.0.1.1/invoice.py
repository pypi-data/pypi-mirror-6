# -*- coding: utf-8 -*-
"""

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from .incoterm import Incoterm

__all__ = ['Invoice', 'InvoiceIncoterm']
__metaclass__ = PoolMeta


class Invoice:
    'Account Invoice Incoterm'
    __name__ = 'account.invoice'

    incoterms = fields.One2Many(
        'account.invoice.incoterm', 'invoice', 'Invoice Incoterm', states={
            'readonly': Eval('state') != 'draft',
        }, depends=['state', 'currency', 'total_amount'],
        context={
            'currency': Eval('currency'),
            'value': Eval('total_amount'),
        }
    )


class InvoiceIncoterm(Incoterm, ModelSQL, ModelView):
    'Invoice Incoterm'
    __name__ = 'account.invoice.incoterm'

    invoice = fields.Many2One('account.invoice', 'Invoice', required=True)
