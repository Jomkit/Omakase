"""Tests for the api"""

# Run tests like:
#
#   python -m unittest tests/test_routes.py
# OR
#   python -m unittest tests.test_routes.BasicRoutesTestCase

import os
import pdb
import models
from flask import get_flashed_messages, session
from flask_login import login_user, logout_user
from unittest import TestCase

# Before importing app, set environmental variable to use a test db for tests
os.environ['DATABASE_URL'] = 'postgresql:///omakase-test'

# Now import app
from app import app
app.config['WTF_CSRF_ENABLED'] = False

# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True
# This will give us the python errors that include traceback,
# Which can be more useful to us for root-cause analysis, but 
# not as pleasant to the user or for debugging as HTML error pages

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables here once for all tests, then in each test we'll delete the data and create fresh new clean data
models.db.drop_all()
models.db.create_all()

class ApiTestCase(TestCase):
    @classmethod 
    def setUpClass(cls):
        db = models.db

        cls.test_restaurant = models.Restaurant(name='test restaurant', address='1 Test St.')

        cls.tables = [
            models.Table(),
            models.Table(),
        ]

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
        db.session.add(cls.test_restaurant)
        db.session.add_all(cls.tables)
        db.session.commit()

        cls.testItem = models.MenuItem(name='test item', meal_type='entree', description='description of test item', cost=9.95, ingredients=[cls.ingredients[1]], intolerants=[cls.intolerants[0]])

        cls.e = models.User(name='test admin', uname='testA1', password=models.User.hash_pw('123test123'), email='test@gmail.com', phone_number='123-456-7890',
            roles=[models.Role.query.filter_by(name='waitstaff').first()],
            groups=[models.Group.query.filter_by(name='employee').first()])
        
        db.session.add_all([cls.e, cls.testItem])
        db.session.commit()

        cls.test_order = models.Order(employee_id=cls.e.id, type='Takeout')
        models.db.session.add(cls.test_order)
        models.db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        db = models.db
        models.Restaurant.query.delete()
        models.Table.query.delete()
        # models.Role.query.delete()
        # models.Group.query.delete()
        models.Ingredient.query.delete()
        models.Intolerant.query.delete()
        models.Order.query.delete()
        models.User.query.delete()
        db.session.commit()
    
    def setUp(self):
        self.client = app.test_client()

    def test_get_all_orders(self):
        resp = self.client.get('/omakase/api/orders')
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn('timestamp', html)

    def test_get_order_by_id(self):
        resp = self.client.get('/omakase/api/order/get_order/1')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('"type": "Takeout"', html)

    def test_post_new_order(self):
        resp = self.client.post('/omakase/api/order/new', 
                                json={
                                    'employee_id': 1,
                                    'table_number': 1,
                                })
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('timestamp', html)        

    def test_patch_update_order_to_inactive(self):
        """Check that the api updates an order by id
        
        3/29/24 - Currently the route only updates order active status
        """
        resp = self.client.patch(f'/omakase/api/order/{self.test_order.id}/update',
                                json={
                                    'data': {
                                        'active': False
                                    }
                                })
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)

    def test_patch_add_to_order(self):
        resp = self.client.patch(f'/omakase/api/order/{self.test_order.id}/add_item',
                                json={
                                    'menu_item_id': self.testItem.id
                                })
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(len(self.test_order.ordered_items), 1)
        self.assertIn('ordered_items', html)

    def test_get_menu_item(self):
        resp = self.client.get(f'omakase/api/menu/get_menu_item/{self.testItem.id}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('"name": "test item"', html)
    
    def test_list_menu_items(self):
        resp = self.client.get('/omakase/api/menu/list_menu_items')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('"name": "test item"', html)