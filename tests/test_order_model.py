"""Tests for order model and related"""

# Run tests like:
#
#   python -m unittest tests/test_models.py
# OR
#   python -m unittest tests.test_models.RestaurantModelTestCase.test_restaurant_model

import os
from unittest import TestCase

from decimal import Decimal
from datetime import date, datetime 
# Before importing app, set environmental variable to use a test db for tests

os.environ['DATABASE_URL'] = 'postgresql:///omakase-test'

# now import app
from app import app
from models.db import db
from models.restaurant_models import Restaurant
from models.user_models import User, Role, Group
from models.item_models import Ingredient, Intolerant, MenuItem
from models.order_models import Table, Order, OrderedItems

# We create our tables here once for all tests, then in each test we'll delete the data and create fresh new clean test data
db.drop_all()
db.create_all()

class OrderModelTestCase(TestCase):
    """Test the Order Model
    Including table model
    """

    @classmethod
    def setUpClass(cls):
        """Set up test data at beginning of TestCase"""

        cls.r = Restaurant(
            name = 'Test Restaurant',
            address = '123 Main Street', 
            phone_number = '123-456-7890'
        )

        cls.ingredients = [
            Ingredient(name='Pasta'),
            Ingredient(name='Test Ingredient'),
        ]

        cls.intolerants = [
            Intolerant(name='Dairy'),
            Intolerant(name='Wheat'),
        ]

        cls.menu_items = [
            MenuItem(name='test_item', meal_type='appetizer',description='test item 1', cost='4.50', 
                ingredients=[cls.ingredients[1]],
                intolerants=[cls.intolerants[0]])
        ]

        db.session.add_all(cls.menu_items)

        db.session.add_all(cls.ingredients)
        db.session.add_all(cls.intolerants)
        db.session.add(cls.r)
        db.session.commit()

        cls.roles = [
            Role(name='waitstaff'),
            Role(name='kitchen'),
            Role(name='manager'),
        ]
        
        cls.groups = [
            Group(name='employee'),
            Group(name='customer'),
        ]
        db.session.add_all(cls.roles)
        db.session.add_all(cls.groups)
        db.session.commit()

        cls.e = User(name='test emp', uname='test123', password='123test123', restaurant_id=cls.r.id, email='test123@gmail.com',address='1 Test Way', birthday='1/1/1990', phone_number='123-456-7890')

        db.session.add(cls.e)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        Restaurant.query.delete()
        MenuItem.query.delete()
        Ingredient.query.delete()
        Intolerant.query.delete()
        User.query.delete()
        Role.query.delete()
        Group.query.delete()
        Table.query.delete()
        Order.query.delete()

        db.session.commit()
        
    def setUp(self):
        db.session.rollback()

        self.test_order = Order(employee_id = self.e.id, type='Takeout')
        self.test_oi = OrderedItems(menu_item_id=self.menu_items[0].id, order_id=self.test_order.id, quantity=2)

        db.session.add(self.test_oi)
        self.test_order.ordered_items.append(self.test_oi)

        db.session.commit()

    def tearDown(self):
        Order.query.delete()
        db.session.commit()

    def test_table_model(self):
        """Does the basic table model work?"""
        tables = [
            Table(taken=False),
            Table(taken=True),
        ]

        db.session.add_all(tables)
        db.session.commit()

        self.assertTrue(tables[1].taken)
        self.assertFalse(tables[0].taken)

    def test_order_model(self):
        """Does the basic order model work?"""
        test_order2 = Order(employee_id = self.e.id, type='Takeout')
        db.session.add(test_order2)
        db.session.commit()

        self.assertIsInstance(test_order2, Order)
        self.assertIsNone(test_order2.table_number)
        self.assertTrue(test_order2.active)
        self.assertIsNone(test_order2.payment_method)
        self.assertIsInstance(test_order2.timestamp, datetime)
        self.assertEqual(test_order2.customers, [])
        self.assertEqual(test_order2.ordered_items, [])

        # Test employee e is assigned to test_order
        self.assertEqual(test_order2.employee_id, self.e.id)
        
        # Test ordered_items
        self.assertEqual(self.test_oi.order_id, self.test_order.id)
        self.assertEqual(self.test_oi.menu_item_id, self.menu_items[0].id)
        self.assertEqual(self.test_oi.quantity, 2)
        
        self.assertEqual(len(self.test_order.ordered_items), 1)    

        self.assertIsInstance(self.test_order.total_cost, Decimal)    
        self.assertNotEqual(self.test_order.total_cost, 0)
        
    def test_order_serialize(self):
        """Does the Order.serialize() class method return a JSON ready format?"""
        serialized = Order.serialize(self.test_order)
        
        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized['id'], self.test_order.id)  
    
    def test_order_create(self):
        """Does Order.create() create new order?"""
        new_order = Order.create(type='Takeout')
        self.assertIsInstance(new_order, Order)
        self.assertEqual(new_order.type, 'Takeout')

    def test_order_update(self):
        """Does Order.update() update an order?"""
        self.assertEqual(self.test_order.type, 'Takeout')
        self.test_order.update({'type': 'Delivery'})
        self.assertEqual(self.test_order.type, 'Delivery')

    def test_order_partial_update(self):
        """Does Order.update() update multiple fields in an order?"""
        self.assertEqual(self.test_order.type, "Takeout")
        self.assertEqual(self.test_order.active, True)

        self.test_order.update({'type': 'Delivery', 'active': False})
        self.assertEqual(self.test_order.type, "Delivery")
        self.assertEqual(self.test_order.active, False)