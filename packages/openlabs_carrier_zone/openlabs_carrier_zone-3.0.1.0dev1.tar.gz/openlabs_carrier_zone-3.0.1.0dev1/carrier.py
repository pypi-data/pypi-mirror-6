# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction

__all__ = ['Carrier', 'CarrierZonePriceList']
__metaclass__ = PoolMeta


class Carrier:
    __name__ = 'carrier'

    zone_currency = fields.Many2One(
        'currency.currency', 'Currency',
        states={
            'invisible': Eval('carrier_cost_method') != 'zone',
            'required': Eval('carrier_cost_method') == 'zone',
            'readonly': Bool(Eval('zone_price_list', [])),
        },
        depends=['carrier_cost_method', 'zone_price_list'])
    zone_price_list = fields.One2Many(
        'carrier.zone_price_list', 'carrier',
        'Price List',
        states={
            'invisible': Eval('carrier_cost_method') != 'zone',
        },
        depends=['carrier_cost_method'])
    zone_currency_digits = fields.Function(
        fields.Integer(
            'Zone Currency Digits', on_change_with=['zone_currency']
        ), 'on_change_with_zone_currency_digits'
    )

    @classmethod
    def __setup__(cls):
        super(Carrier, cls).__setup__()
        selection = ('zone', 'Zone')
        if selection not in cls.carrier_cost_method.selection:
            cls.carrier_cost_method.selection.append(selection)

    def on_change_with_zone_currency_digits(self, name=None):
        if self.zone_currency:
            return self.zone_currency.digits
        return 2

    def get_sale_price(self):
        Address = Pool().get('party.address')
        ZonePriceList = Pool().get('carrier.zone_price_list')

        price, currency_id = super(Carrier, self).get_sale_price()
        if self.carrier_cost_method == 'zone':
            zone = None
            if 'address' in Transaction().context:
                zone = self.find_zone_for_address(
                    Address(Transaction().context['address'])
                )
            elif 'zone' in Transaction().context:
                zone, = ZonePriceList.search([
                    ('carrier', '=', self.id),
                    ('id', '=', Transaction().context['zone']),
                ])
            if zone is not None:
                return zone.price, self.zone_currency.id
        return price, currency_id

    def get_purchase_price(self):
        Address = Pool().get('party.address')
        ZonePriceList = Pool().get('carrier.zone_price_list')

        price, currency_id = super(Carrier, self).get_purchase_price()
        if self.carrier_cost_method == 'zone':
            zone = None
            if 'address' in Transaction().context:
                zone = self.find_zone_for_address(
                    Address(Transaction().context['address'])
                )
            elif 'zone' in Transaction().context:
                zone, = ZonePriceList.search([
                    ('carrier', '=', self.id),
                    ('id', '=', Transaction().context['zone']),
                ])
            if zone is not None:
                return zone.price, self.zone_currency.id
        return price, currency_id

    def find_zone_for_address(self, address):
        """
        A helper function that finds the most matching zone from the given
        address.

        :param address: Active Record of the address
        :return: Active Record of the zone_price_list
        """
        CarrierZone = Pool().get('carrier.zone_price_list')

        zones = CarrierZone.search([
            ('country', '=', address.country),
            ('subdivision', '=', address.subdivision),
        ], limit=1)

        if not zones:
            zones = CarrierZone.search([
                ('country', '=', address.country),
                ('subdivision', '=', None),
            ], limit=1)

        if zones:
            return zones[0]


class CarrierZonePriceList(ModelSQL, ModelView):
    'Carrier Zone price List'
    __name__ = 'carrier.zone_price_list'

    carrier = fields.Many2One('carrier', 'Carrier', required=True, select=True)
    country = fields.Many2One(
        'country.country', 'Country', required=True, select=True
    )
    subdivision = fields.Many2One(
        'country.subdivision', 'Subdivision', select=True,
        domain=[('country', '=', Eval('country'))],
        depends=['country']
    )
    price = fields.Numeric(
        'Price', digits=(16, Eval('_parent_carrier.weight_currency_digits', 2))
    )

    # TODO add a sequence and order by sequence
