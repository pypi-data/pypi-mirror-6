# -*- coding: utf-8 -*-
"""

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta
from .incoterm import Incoterm

__all__ = ['Invoice', 'InvoiceIncoterm']
__metaclass__ = PoolMeta


class Invoice:
    'Account Invoice Incoterm'
    __name__ = 'account.invoice'

    incoterms = fields.One2Many(
        'account.invoice.incoterm', 'invoice', 'Invoice Incoterm'
    )


class InvoiceIncoterm(Incoterm, ModelSQL, ModelView):
    'Invoice Incoterm'
    __name__ = 'account.invoice.incoterm'

    invoice = fields.Many2One('account.invoice', 'Invoice', required=True)
