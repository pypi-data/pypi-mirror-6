# -*- coding: utf-8 -*-
"""
    test_carrier

    Test carrier logic.

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.transaction import Transaction
from trytond.tests.test_tryton import POOL, DB_NAME, CONTEXT, USER


class TestCarrier(unittest.TestCase):
    '''
    Test carrier
    '''
    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('carrier_zone')

    def create_carrier(self):
        '''
        Create the carrier
        '''
        Carrier = POOL.get('carrier')
        ProductTemplate = POOL.get('product.template')
        Product = POOL.get('product.product')
        UOM = POOL.get('product.uom')
        Currency = POOL.get('currency.currency')
        Party = POOL.get('party.party')

        party, = Party.create([{
            'name': 'Carrier',
        }])
        usd = Currency(
            name='US Dollar', symbol="$", code="USD"
        )
        usd.save()

        template, = ProductTemplate.create([{
            'name': 'Carrier',
            'default_uom': UOM.search([
                ('name', '=', 'Unit'),
            ])[0].id,
            'type': 'service',
            'list_price': Decimal(0),
            'cost_price': Decimal(0),
        }])
        product, = Product.create([{
            'template': template.id,
        }])

        carrier, = Carrier.create([{
            'zone_currency': usd,
            'carrier_product': product.id,
            'party': party.id,
        }])

        return carrier

    def test0010createzone(self):
        '''
        Create a zone and pricelist for it
        '''
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            Country = POOL.get('country.country')
            CarrierZonePriceList = POOL.get('carrier.zone_price_list')

            carrier = self.create_carrier()

            united_states, = Country.create([{
                'name': 'United States',
                'code': 'US',
            }])
            CarrierZonePriceList.create([{
                'carrier': carrier.id,
                'country': united_states.id,
                'price': Decimal('100'),
            }])

    def test0020priceonaddress(self):
        '''
        Ensure that the right zone is found
        '''
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            CarrierZonePriceList = POOL.get('carrier.zone_price_list')
            Country = POOL.get('country.country')
            Subdivision = POOL.get('country.subdivision')
            Address = POOL.get('party.address')

            carrier = self.create_carrier()

            united_states, india = Country.create([
                {
                    'name': 'United States',
                    'code': 'US',
                },
                {
                    'name': 'India',
                    'code': 'IN',
                },
            ])

            california, colorado = Subdivision.create([
                {
                    'country': united_states.id,
                    'name': 'Calfornia',
                    'code': 'CA',
                    'type': 'state'
                },
                {
                    'country': united_states.id,
                    'name': 'Colorado',
                    'code': 'CO',
                    'type': 'state'
                },
            ])

            uttar_pradesh, = Subdivision.create([
                {
                    'country': india.id,
                    'name': 'Uttar Pradesh',
                    'code': 'UP',
                    'type': 'state'
                },
            ])

            zone_in_all, = CarrierZonePriceList.create([
                {
                    'carrier': carrier.id,
                    'country': india.id,
                    'price': Decimal('100'),
                },

            ])
            zone_us_ca, = CarrierZonePriceList.create([
                {
                    'carrier': carrier.id,
                    'country': united_states.id,
                    'subdivision': california.id,
                    'price': Decimal('100'),
                }
            ])

            # Get a perfect match on state and country
            zone = carrier.find_zone_for_address(
                Address(
                    country=united_states.id,
                    subdivision=california.id,
                )
            )
            self.assertTrue(zone)
            self.assertEqual(zone.country.id, united_states.id)
            self.assertEqual(zone.subdivision.id, california.id)

            # no record with given subdivision or subdivision=None
            zone = carrier.find_zone_for_address(
                Address(
                    country=united_states.id,
                    subdivision=colorado.id,
                )
            )
            self.assertFalse(zone)

            # Get a match of zone for state that doesn't exist in list
            # but a record exist where subdivsion isn't set
            zone = carrier.find_zone_for_address(
                Address(
                    country=india.id,
                    subdivision=uttar_pradesh.id,
                )
            )
            self.assertTrue(zone)
            self.assertEqual(zone.country.id, india.id)
            self.assertFalse(zone.subdivision)


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCarrier)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
