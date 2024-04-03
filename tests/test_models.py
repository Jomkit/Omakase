"""Tests for the models"""

# Run tests like:
#
#   python -m unittest tests/test_models.py
# OR
#   python -m unittest tests.test_models.RestaurantModelTestCase.test_restaurant_model

import os
from unittest import TestCase

import models
from decimal import Decimal
from datetime import date, datetime 
# Before importing app, set environmental variable to use a test db for tests

os.environ['DATABASE_URL'] = 'postgresql:///omakase-test'

# now import app

from app import app

# We create our tables here once for all tests, then in each test we'll delete the data and create fresh new clean test data
models.db.drop_all()
models.db.create_all()

class RestaurantModelTestCase(TestCase):
    """Test the Restaurant Model"""

    @classmethod
    def setUpClass(cls):
        """Set up test data at beginning of TestCase"""
        db = models.db

        cls.r = models.Restaurant(
            name = 'Test Restaurant',
            address = '123 Main Street', 
            phone_number = '123-456-7890'
        )

        db.session.add(cls.r)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        models.Restaurant.query.delete()
        models.db.session.commit()
        
    def setUp(self):
        """Create test client, and add sample restaurant"""
        models.db.session.rollback()
        models.User.query.delete()

        self.e = models.User(restaurant_id=self.r.id, name='Test', address='1 Test Rd', birthday='1/1/1990', roles=[])

        models.db.session.add(self.e)
        models.db.session.commit()

    def test_restaurant_model(self):
        """Does the basic restaurant model work?"""

        r = self.r
        
        self.assertIsInstance(r, models.Restaurant)       
        self.assertEqual(r.name, 'Test Restaurant')
        self.assertEqual(r.address, '123 Main Street')
        self.assertEqual(r.phone_number, '123-456-7890')
        self.assertEqual(len(r.employees), 1)
        self.assertEqual(len(r.menu), 0)

class UserModelTestCase(TestCase):
    """Test the User Model"""

    @classmethod
    def setUpClass(cls):
        """Set up test data at beginning of TestCase"""
        db = models.db

        cls.r = models.Restaurant(
            name = 'Test Restaurant',
            address = '123 Main Street', 
            phone_number = '123-456-7890'
        )
        cls.roles = [
            models.Role(name='waitstaff'),
            models.Role(name='kitchen'),
            models.Role(name='admin'),
        ]
        
        cls.groups = [
            models.Group(name='employee'),
            models.Group(name='customer'),
        ]

        cls.ingredients = [
            models.Ingredient(name='Pasta'),
            models.Ingredient(name='Test Ingredient'),
        ]

        cls.intolerants = [
            models.Intolerant(name='Dairy'),
            models.Intolerant(name='Wheat'),
        ]
        db.session.add_all(cls.ingredients)
        db.session.add_all(cls.intolerants)
        
        db.session.add_all(cls.roles)
        db.session.add_all(cls.groups)
        db.session.add(cls.r)
        db.session.commit()
        
    @classmethod
    def tearDownClass(cls):
        models.Restaurant.query.delete()
        models.User.query.delete()
        models.MenuItem.query.delete()
        models.Role.query.delete()
        models.Group.query.delete()
        models.Ingredient.query.delete()
        models.Intolerant.query.delete()
        
        models.db.session.commit()
        
    def setUp(self):
        """Create test client, and add sample restaurant"""
        models.db.session.rollback()
        models.User.query.delete()

        self.e = models.User(restaurant_id=models.db.session.query(models.Restaurant.id).first(), name='Test', address='1 Test Rd', birthday='1/1/1990')

        models.db.session.add(self.e)
        models.db.session.commit()

    def test_user_model(self):
        """Does the basic User model work?"""

        e = models.User(restaurant_id=models.db.session.query(models.Restaurant.id).first(), name='Test Guy', address='12 Test Rd', birthday='2/2/1990', password=models.User.hash_pw('123test123'), email='test@gmail.com', phone_number='123-456-7890',
        roles=[models.Role.query.filter_by(name='waitstaff').first()],
        groups=[models.Group.query.filter_by(name='employee').first()]
        )
        models.db.session.add(e)
        models.db.session.commit()

        self.assertIsInstance(e, models.User)
        self.assertEqual(e.name, 'Test Guy')
        self.assertFalse(e.temp)
        self.assertEqual(e.username, f'TestGuy{e.id}')
        self.assertEqual(e.uname, f'TestGuy{e.id}')
        self.assertIsInstance(e.restaurant_id, int)
        self.assertEqual(len(self.r.employees), 2)
        self.assertEqual(e.email, 'test@gmail.com')
        self.assertEqual(e.address, '12 Test Rd')
        self.assertIsInstance(e.birthday, date)
        self.assertEqual(str(e.birthday), '1990-02-02')
        self.assertEqual(e.phone_number, '123-456-7890')
        self.assertEqual(e.roles[0].name, 'waitstaff')
        self.assertEqual(e.groups[0].name, 'employee')

        self.assertNotEqual('testpw123', models.User.hash_pw('testpw123'))
        self.assertIsInstance(models.User.Authenticate(e.uname, '123test123'), models.User)

class MenuItemModelTestCase(TestCase):
    """Test the MenuItem Model"""

    @classmethod
    def setUpClass(cls):
        """Set up test data at beginning of TestCase"""
        db = models.db

        cls.r = models.Restaurant(
            name = 'Test Restaurant',
            address = '123 Main Street', 
            phone_number = '123-456-7890'
        )

        cls.ingredients = [
            models.Ingredient(name='Pasta'),
            models.Ingredient(name='Test Ingredient'),
        ]

        cls.intolerants = [
            models.Intolerant(name='Dairy'),
            models.Intolerant(name='Wheat'),
        ]

        db.session.add_all(cls.ingredients)
        db.session.add_all(cls.intolerants)
        db.session.add(cls.r)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        models.Restaurant.query.delete()
        models.MenuItem.query.delete()
        models.Ingredient.query.delete()
        models.Intolerant.query.delete()

        models.db.session.commit()
        
    def setUp(self):
        models.db.session.rollback()
        
        self.client = app.test_client()
    def test_menu_item(self):
        """Does basic MenuItem model work?"""
        
        mi = models.MenuItem(
                name = 'Spaghetti & Meatballs', 
                meal_type = 'Entree',
                description = 'Test Spaghetti & Meatballs',
                cost=13.95,
                ingredients=[models.Ingredient.query.filter_by(name='Pasta').first()],
                intolerants=[models.Intolerant.query.filter_by(name='Dairy').first()],
            )
        
        
        models.db.session.add(mi)
        models.db.session.commit()

        self.assertIsInstance(mi, models.MenuItem)
        self.assertEqual(mi.name, 'Spaghetti & Meatballs')
        self.assertEqual(mi.image, '/static/images/food_placeholder.png')
        self.assertEqual(mi.meal_type, 'Entree')
        self.assertTrue(mi.in_stock)
        self.assertFalse(mi.vegetarian)
        self.assertIsInstance(mi.description, str)
        self.assertIsInstance(mi.cost, Decimal)

        self.assertEqual(mi.ingredients[0].name, 'Pasta')
        self.assertEqual(mi.intolerants[0].name, 'Dairy')

        # Test add_ingredients class method
        mi_ingr_added = models.MenuItem.add_ingredients(['Test Ingredient'], mi.id)
        self.assertIsInstance(mi_ingr_added, models.MenuItem)

        # Test add_intolerants class method
        mi_int_added = models.MenuItem.add_intolerants(['Test Intolerant'], mi.id)
        self.assertIsInstance(mi_int_added, models.MenuItem)

        # Test serialize class method
        serial_mi = models.MenuItem.serialize(mi)
        self.assertIsInstance(serial_mi, dict)
        self.assertEqual(serial_mi['id'], mi.id)

    def test_ingredient(self):
        """Does basic ingredient model work?"""
        ingr = models.Ingredient(name='test ingredient 2')
        models.db.session.add(ingr)
        models.db.session.commit()

        self.assertIsInstance(ingr, models.Ingredient)

    def test_intolerant(self):
        """Does basic intolerant model work?"""
        intol = models.Intolerant(name='test intolerant')
        models.db.session.add(intol)
        models.db.session.commit()

        self.assertIsInstance(intol, models.Intolerant)
    
class OrderModelTestCase(TestCase):
    """Test the Order Model
    Including table model
    """

    @classmethod
    def setUpClass(cls):
        """Set up test data at beginning of TestCase"""
        db = models.db

        cls.r = models.Restaurant(
            name = 'Test Restaurant',
            address = '123 Main Street', 
            phone_number = '123-456-7890'
        )

        cls.ingredients = [
            models.Ingredient(name='Pasta'),
            models.Ingredient(name='Test Ingredient'),
        ]

        cls.intolerants = [
            models.Intolerant(name='Dairy'),
            models.Intolerant(name='Wheat'),
        ]

        cls.menu_items = [
            models.MenuItem(name='test_item', meal_type='appetizer',description='test item 1', cost='4.50', 
                ingredients=[cls.ingredients[1]],
                intolerants=[cls.intolerants[0]])
        ]

        db.session.add_all(cls.menu_items)

        db.session.add_all(cls.ingredients)
        db.session.add_all(cls.intolerants)
        db.session.add(cls.r)
        db.session.commit()

        cls.roles = [
            models.Role(name='waitstaff'),
            models.Role(name='kitchen'),
            models.Role(name='admin'),
        ]
        
        cls.groups = [
            models.Group(name='employee'),
            models.Group(name='customer'),
        ]
        db.session.add_all(cls.roles)
        db.session.add_all(cls.groups)
        db.session.commit()

        cls.e = models.User(name='test emp', uname='test123', password='123test123', restaurant_id=cls.r.id, email='test123@gmail.com',address='1 Test Way', birthday='1/1/1990', phone_number='123-456-7890')

        db.session.add(cls.e)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        models.Restaurant.query.delete()
        models.MenuItem.query.delete()
        models.Ingredient.query.delete()
        models.Intolerant.query.delete()
        models.User.query.delete()
        models.Role.query.delete()
        models.Group.query.delete()
        models.Table.query.delete()
        models.Order.query.delete()

        models.db.session.commit()
        
    def setUp(self):
        models.db.session.rollback()

        self.test_order = models.Order(employee_id = self.e.id, type='Takeout')
        self.test_oi = models.OrderedItems(menu_item_id=self.menu_items[0].id, order_id=self.test_order.id, quantity=2)

        models.db.session.add(self.test_oi)
        self.test_order.ordered_items.append(self.test_oi)

        models.db.session.commit()

    def tearDown(self):
        models.Order.query.delete()
        models.db.session.commit()

    def test_table_model(self):
        """Does the basic table model work?"""
        tables = [
            models.Table(taken=False),
            models.Table(taken=True),
        ]

        models.db.session.add_all(tables)
        models.db.session.commit()

        self.assertTrue(tables[1].taken)
        self.assertFalse(tables[0].taken)

    def test_order_model(self):
        """Does the basic order model work?"""
        test_order2 = models.Order(employee_id = self.e.id, type='Takeout')
        models.db.session.add(test_order2)
        models.db.session.commit()

        self.assertIsInstance(test_order2, models.Order)
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
        serialized = models.Order.serialize(self.test_order)
        
        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized['id'], self.test_order.id)  
