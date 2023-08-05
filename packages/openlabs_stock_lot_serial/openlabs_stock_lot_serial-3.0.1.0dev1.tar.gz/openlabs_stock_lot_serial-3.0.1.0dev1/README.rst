Tryton Serialized Inventory Control
===================================

This module adds a serialized inventory control field to product, which is used
by stock shipments while accepting incoming moves. If serialized inventory
control is set for a product, the quantity of the product can't be greater than
one for incoming moves. Such moves however can be splitted using "Split" button
provided by this module in shipment form. Each incoming move with quantity 'n'
will be replaced by 'n' new incoming moves each with quantity equal to one.
