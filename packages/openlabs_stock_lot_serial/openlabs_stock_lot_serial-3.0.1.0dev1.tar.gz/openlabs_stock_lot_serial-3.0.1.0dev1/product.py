# -*- coding: utf-8 -*-
"""
    stock_lot_serial.product

    Product

    :copyright: (c) 2013-2014 by Openlabs Technologies & Consulting (P) Limited
    :license: 3-clause BSD, see LICENSE for more details.
"""
from trytond.model import fields
from trytond.pool import PoolMeta

__metaclass__ = PoolMeta
__all__ = ['Template']


class Template:
    "Product Model"
    __name__ = 'product.template'

    serialized_inventory_control = fields.Boolean(
        'Serialized Inventory Control?'
    )
