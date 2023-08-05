# -*- coding: utf-8 -*-
"""
    stock_lot_serial.stock

    Shipment

    :copyright: (c) 2013-2014 by Openlabs Technologies & Consulting (P) Limited
    :license: 3-clause BSD, see LICENSE for more details.
"""
from trytond.model import ModelView
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval

__metaclass__ = PoolMeta
__all__ = ['ShipmentIn']


class ShipmentIn:
    "ShipmentIn"
    __name__ = "stock.shipment.in"

    @classmethod
    def __setup__(cls):
        super(ShipmentIn, cls).__setup__()
        cls._buttons.update({
            'split_moves': {
                'invisible': Eval('state') != 'draft',
            },
        })

    def _split_moves(self):
        "Split incoming moves with quantity greater than 1"
        Move = Pool().get('stock.move')

        for move in self.incoming_moves:
            if not move.product.serialized_inventory_control:
                continue
            while move.quantity > 1:
                Move.copy([move], {'quantity': 1, 'lot': None})
                move.quantity -= 1
            move.save()

    @classmethod
    @ModelView.button
    def split_moves(cls, shipments):
        "Split incoming moves with quantity greater than 1"
        for shipment in shipments:
            shipment._split_moves()


class Move:
    "Move"
    __name__ = "stock.move"

    @classmethod
    def __setup__(cls):
        super(Move, cls).__setup__()
        cls._error_messages.update({
            'quantity_one': "Quantity for moves with products having serialized"
                            " inventory control cannot be greater than 1."
        })

    def check_product_serial(self):
        """
        Ensure that products with serialized inventory control have only 1 as
        quantity for stock moves.
        """
        if self.state == 'done' and \
            self.product.template.serialized_inventory_control and \
                self.quantity != 1.0:
            self.raise_user_error('quantity_one')

    @classmethod
    def validate(cls, moves):
        """
        Check if quantity is one when serialized inventory control is true for
        each incoming move
        """
        super(Move, cls).validate(moves)
        for move in moves:
            move.check_product_serial()
