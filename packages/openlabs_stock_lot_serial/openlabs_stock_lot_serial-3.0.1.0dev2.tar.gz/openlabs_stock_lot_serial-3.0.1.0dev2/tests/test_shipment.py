# -*- coding: utf-8 -*-
"""
    stock_lot_serial.tests.test_shipment

    Test Shipment

    :copyright: (c) 2013-2014 by Openlabs Technologies & Consulting (P) Limited
    :license: 3-clause BSD, see LICENSE for more details.
"""
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class TestShipmentIn(unittest.TestCase):
    '''
    Test shipment
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('stock_lot_serial')

    def create_defaults(self):
        "Create defaults"
        Template = POOL.get('product.template')
        Product = POOL.get('product.product')
        Uom = POOL.get('product.uom')
        Party = POOL.get('party.party')
        User = POOL.get('res.user')
        Company = POOL.get('company.company')
        Lot = POOL.get('stock.lot')
        LotType = POOL.get('stock.lot.type')

        party, = Party.create([{'name': 'testuser'}])
        self.assert_(party.id)

        Currency = POOL.get('currency.currency')
        currency = Currency(
            name='Euro', symbol=u'€', code='EUR',
            rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
            mon_decimal_point=','
        )
        currency.save()
        company, = Company.create([{
            'party': party.id,
            'currency': currency
        }])
        company2, = Company.create([{
            'party': party.id,
            'currency': currency
        }])

        User.write(
            [User(USER)], {
                'main_company': company.id,
                'company': company.id,
            }
        )

        lot_type, = LotType.search([('name', '=', 'Supplier')])
        uom, = Uom.search([('name', '=', 'Unit')])
        template1, = Template.create([{
            'name': 'product',
            'type': 'goods',
            'list_price': Decimal('20'),
            'cost_price': Decimal('5'),
            'default_uom': uom,
            'serialized_inventory_control': False,
            'lot_required': [('set', [lot_type.id])]
        }])

        template2, = Template.create([{
            'name': 'product',
            'type': 'goods',
            'list_price': Decimal('20'),
            'cost_price': Decimal('5'),
            'default_uom': uom,
            'serialized_inventory_control': True,
            'lot_required': [('set', [lot_type.id])]
        }])

        product1, = Product.create([{
            'template': template1.id,
        }])
        lot1, = Lot.create([{
            'number': 'LN01',
            'product': product1.id,
        }])

        product2, = Product.create([{
            'template': template2.id,
        }])
        lot2, = Lot.create([{
            'number': 'LN02',
            'product': product2.id,
        }])

        return {
            'party': party,
            'company': company,
            'currency': currency,
            'uom': uom,
            'product1': product1,
            'template1': template1,
            'lot1': lot1,
            'product2': product2,
            'template2': template2,
            'lot2': lot2,
        }

    def _create_non_serialized_product_shipment(self, defaults):
        "Create a shipment with product that has inventory control set to false"
        ShipmentIn = POOL.get('stock.shipment.in')
        Location = POOL.get('stock.location')

        supplier, = Location.search([('code', '=', 'SUP')])
        warehouse, = Location.search([('code', '=', 'WH')])
        inputzone, = Location.search([('code', '=', 'IN')])
        shipment, = ShipmentIn.create([{
            'company': defaults['company'],
            'supplier': defaults['party'],
            'warehouse': warehouse.id,
            'moves': [('create', [{
                'product': defaults['product1'],
                'uom': defaults['uom'],
                'from_location': supplier,
                'to_location': inputzone,
                'company': defaults['company'],
                'quantity': 3.0,
                'currency': defaults['currency'],
                'unit_price': Decimal(2.0),
                'lot': defaults['lot1'].id,
            }])],
        }])
        return shipment

    def _create_serialized_move_shipment(self, defaults):
        """
        Create a shipment with product that has inventory control set to true
        and move with quantity greater than 1
        """
        ShipmentIn = POOL.get('stock.shipment.in')
        Location = POOL.get('stock.location')

        supplier, = Location.search([('code', '=', 'SUP')])
        warehouse, = Location.search([('code', '=', 'WH')])
        inputzone, = Location.search([('code', '=', 'IN')])
        shipment, = ShipmentIn.create([{
            'company': defaults['company'],
            'supplier': defaults['party'],
            'warehouse': warehouse.id,
            'moves': [('create', [{
                'product': defaults['product2'],
                'uom': defaults['uom'],
                'from_location': supplier,
                'to_location': inputzone,
                'company': defaults['company'],
                'quantity': 3.0,
                'currency': defaults['currency'],
                'unit_price': Decimal(2.0),
                'lot': defaults['lot2'].id,
            }])]
        }])
        return shipment

    def _create_mixed_serialized_shipment(self, defaults):
        '''
        Create a shipment with both serialized and non-serialized inventory
        controlled products
        '''
        ShipmentIn = POOL.get('stock.shipment.in')
        Location = POOL.get('stock.location')

        supplier, = Location.search([('code', '=', 'SUP')])
        warehouse, = Location.search([('code', '=', 'WH')])
        inputzone, = Location.search([('code', '=', 'IN')])
        shipment, = ShipmentIn.create([{
            'company': defaults['company'],
            'supplier': defaults['party'],
            'warehouse': warehouse.id,
            'moves': [('create', [
                {
                    'product': defaults['product1'],
                    'uom': defaults['uom'],
                    'from_location': supplier,
                    'to_location': inputzone,
                    'company': defaults['company'],
                    'quantity': 3.0,
                    'currency': defaults['currency'],
                    'unit_price': Decimal(2.0),
                    'lot': defaults['lot1'].id,
                },
                {
                    'product': defaults['product2'],
                    'uom': defaults['uom'],
                    'from_location': supplier,
                    'to_location': inputzone,
                    'company': defaults['company'],
                    'quantity': 3.0,
                    'currency': defaults['currency'],
                    'unit_price': Decimal(2.0),
                    'lot': defaults['lot2'].id,
                },
            ])]
        }])
        return shipment

    def test0010incoming_move_serialized(self):
        '''
        Tests receiving of shipment having product with serialized inventory
        control
        '''
        Location = POOL.get('stock.location')
        ShipmentIn = POOL.get('stock.shipment.in')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            defaults = self.create_defaults()
            supplier, = Location.search([('code', '=', 'SUP')])
            warehouse, = Location.search([('code', '=', 'WH')])
            inputzone, = Location.search([('code', '=', 'IN')])

            # Shipment with product serialized inventory control = true
            shipment1 = self._create_non_serialized_product_shipment(defaults)
            self.assertTrue(shipment1.id)

            # should not throw exception as serialized_inventory_control is
            # set to false in product
            ShipmentIn.receive([shipment1])

    def test0020incoming_move_non_serialized_no_split(self):
        '''
        Tests receiving of shipment having product with non-serialized inventory
        control
        '''
        Location = POOL.get('stock.location')
        ShipmentIn = POOL.get('stock.shipment.in')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            defaults = self.create_defaults()
            supplier, = Location.search([('code', '=', 'SUP')])
            warehouse, = Location.search([('code', '=', 'WH')])
            inputzone, = Location.search([('code', '=', 'IN')])

            # Shipment with product serialized inventory control = false and
            # quantity > 1
            shipment2 = self._create_serialized_move_shipment(defaults)

            with self.assertRaises(UserError):
                # Try to recieve shipment2. Since, serialized_inventory_control
                # is set true for product and quantity is greater than 1,
                # UserError should be raised.
                ShipmentIn.receive([shipment2])

    def test0030incoming_move_non_serialized_split(self):
        '''
        Test splitting of moves in shipment
        '''
        Location = POOL.get('stock.location')
        ShipmentIn = POOL.get('stock.shipment.in')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            defaults = self.create_defaults()
            supplier, = Location.search([('code', '=', 'SUP')])
            warehouse, = Location.search([('code', '=', 'WH')])
            inputzone, = Location.search([('code', '=', 'IN')])

            # Shipment with product serialized inventory control = false and
            # quantity > 1
            shipment3 = self._create_serialized_move_shipment(defaults)
            # first check if every move has expected value
            self.assertEqual(len(shipment3.incoming_moves), 1)
            move_original_id = shipment3.incoming_moves[0].id

            for move in shipment3.incoming_moves:
                self.assertEqual(move.quantity, 3.0)

            ShipmentIn.split_moves([shipment3])
            shipment3 = ShipmentIn(shipment3.id)
            self.assertEqual(len(shipment3.incoming_moves), 3)

            for move in shipment3.incoming_moves:
                self.assertEqual(move.quantity, 1.0)
                if move.id != move_original_id:
                    self.assertFalse(move.lot)

    def test0040incoming_move_mixed_receive(self):
        '''
        Test shipment with both serialized and non-serialized shipments
        '''
        Location = POOL.get('stock.location')
        ShipmentIn = POOL.get('stock.shipment.in')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            defaults = self.create_defaults()
            supplier, = Location.search([('code', '=', 'SUP')])
            warehouse, = Location.search([('code', '=', 'WH')])
            inputzone, = Location.search([('code', '=', 'IN')])

            shipment = self._create_mixed_serialized_shipment(defaults)
            # first check if every move has expected value
            self.assertEqual(len(shipment.incoming_moves), 2)

            with self.assertRaises(UserError):
                ShipmentIn.receive([shipment])

    def test0040incoming_move_mixed_split(self):
        '''
        Test shipment with both serialized and non-serialized shipments
        '''
        Location = POOL.get('stock.location')
        ShipmentIn = POOL.get('stock.shipment.in')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            defaults = self.create_defaults()
            supplier, = Location.search([('code', '=', 'SUP')])
            warehouse, = Location.search([('code', '=', 'WH')])
            inputzone, = Location.search([('code', '=', 'IN')])

            shipment = self._create_mixed_serialized_shipment(defaults)
            # first check if every move has expected value
            self.assertEqual(len(shipment.incoming_moves), 2)

            ShipmentIn.split_moves([shipment])
            self.assertEqual(len(shipment.incoming_moves), 4)

            for move in shipment.incoming_moves:
                if move.product.serialized_inventory_control:
                    self.assertEqual(move.quantity, 1.0)


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestShipmentIn)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
