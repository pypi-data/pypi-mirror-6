# -*- coding: utf-8 -*-
"""
    incoterm

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from trytond.model import fields
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Incoterm']

YEARS = [
    ('2000', '2000'),
    ('2010', '2010'),
]
ABBREVATIONS = [
    (None, ''),
    ('EXW', 'EXW - Ex Works'),
    ('CPT', 'CPT - Carriage Paid To'),
    ('CIP', 'CIP - Carrier and Insurance Paid to'),
    ('DAT', 'DAT - Delivered at Terminal'),
    ('DAP', 'DAP - Delivered at Place'),
    ('FAS', 'FAS - Free Alongside Ship'),
    ('FOB', 'FOB - Free on Board'),
    ('CFR', 'CFR - Cost and Freight'),
    ('CIF', 'CIF - Cost, Insurance and Freight'),
    ('DAF', 'DAF - Delivered at Frontier'),
    ('DES', 'DES - Delivered Ex Ship'),
    ('DEQ', 'DEQ - Delievered Ex Quay'),
    ('DDU', 'DDU - Delivered Duty Unpaid'),
]


class Incoterm(object):
    'Incoterm Mixin'

    year = fields.Selection(YEARS, 'Year', select=True, required=True)
    abbrevation = fields.Selection(
        ABBREVATIONS, 'Abbrevation', select=True, required=True
    )
    value = fields.Numeric(
        'Value', digits=(16, Eval('currency_digits', 2)),
        depends=['currency_digits']
    )
    currency = fields.Many2One('currency.currency', 'Currency')
    city = fields.Char('City', required=True)
    currency_digits = fields.Function(
        fields.Integer('Value', on_change_with=['currency'],
            depends=['currency']
        ), 'on_change_with_currency'
    )

    def get_rec_name(self, name):
        return "%s -(Incoterm %s)" % (self.abbrevation, self.year)

    @staticmethod
    def default_year():
        return '2010'

    @staticmethod
    def default_currency():
        Company = Pool().get('company.company')

        if 'currency' in Transaction().context:
            return Transaction().context.get('currency')

        company_id = Transaction().context.get('company')
        if company_id:
            return Company(company_id).currency.id
        return None

    def on_change_with_currency(self, name=None):
        if self.currency:
            return self.currency.digits
        return 2

    @staticmethod
    def default_value():
        return Transaction().context.get('value')
