# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""

from trytond.pool import PoolMeta

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = "sale.sale"

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        if 'shipment_address' not in cls.carrier.on_change:
            cls.carrier.on_change.append('shipment_address')
        if 'shipment_address' not in cls.lines.on_change:
            cls.lines.on_change.append('shipment_address')

    def _get_carrier_context(self):
        "Add zone to carrier context"
        context = super(Sale, self)._get_carrier_context()

        if not self.carrier:
            return context
        elif self.carrier.carrier_cost_method != 'zone':
            return context

        if self.shipment_address:
            context['address'] = self.shipment_address.id

        return context
