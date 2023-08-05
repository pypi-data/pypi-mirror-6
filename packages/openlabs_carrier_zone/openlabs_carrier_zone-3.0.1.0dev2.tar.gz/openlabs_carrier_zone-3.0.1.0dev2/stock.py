# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""

from trytond.pool import PoolMeta

__all__ = ['ShipmentOut']
__metaclass__ = PoolMeta


class ShipmentOut:
    __name__ = "stock.shipment.out"

    @classmethod
    def __setup__(cls):
        super(ShipmentOut, cls).__setup__()
        if 'delivery_address' not in cls.carrier.on_change:
            cls.carrier.on_change.append('delivery_address')
        if 'delivery_address' not in cls.inventory_moves.on_change:
            cls.inventory_moves.on_change.append('delivery_address')

    def _get_carrier_context(self):
        "Add zone to carrier context"
        context = super(ShipmentOut, self)._get_carrier_context()

        if not self.carrier:
            return context
        elif self.carrier.carrier_cost_method != 'zone':
            return context

        if self.delivery_address:
            context['address'] = self.delivery_address.id

        return context
