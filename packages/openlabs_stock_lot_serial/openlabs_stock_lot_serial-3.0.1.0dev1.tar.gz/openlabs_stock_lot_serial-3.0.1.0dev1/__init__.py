# -*- coding: utf-8 -*-
"""
    __init__

    :copyright: (c) 2013-2014 by Openlabs Technologies & Consulting (P) Limited
    :license: 3-clause BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from product import Template
from stock import ShipmentIn, Move


def register():
    Pool.register(
        Template,
        Move,
        ShipmentIn,
        module='stock_lot_serial', type_='model'
    )
