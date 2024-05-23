"""Tests for the routes"""

# Run tests like:
#
#   python -m unittest tests/test_routes.py
# OR
#   python -m unittest tests.test_routes.BasicRoutesTestCase

import os
# from dotenv import load_env
from flask import get_flashed_messages, session
from flask_login import login_user, logout_user
from unittest import TestCase

# Before importing app, set environmental variable to use a test db for tests
os.environ['DATABASE_URL'] = 'postgresql:///omakase-test'

# import models
from models.db import db
from models.restaurant_models import Restaurant
from models.user_models import Role, Group, User
from models.order_models import Table, Order
from models.item_models import Ingredient, Intolerant

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
db.drop_all()
db.create_all()

class BasicRoutesTestCase(TestCase):
    @classmethod 
    def setUpClass(cls):
        cls.test_restaurant = Restaurant(name='test restaurant', address='1 Test St.')

        cls.tables = [
            Table(),
            Table(),
        ]

        cls.roles = [
            Role(name='waitstaff'),
            Role(name='kitchen'),
            Role(name='manager'),
        ]
        
        cls.groups = [
            Group(name='employee'),
            Group(name='customer'),
        ]

        cls.ingredients = [
            Ingredient(name='Pasta'),
            Ingredient(name='Test Ingredient'),
        ]

        cls.intolerants = [
            Intolerant(name='Dairy'),
            Intolerant(name='Wheat'),
        ]
        db.session.add_all(cls.ingredients)
        db.session.add_all(cls.intolerants)
        
        db.session.add_all(cls.roles)
        db.session.add_all(cls.groups)
        db.session.add(cls.test_restaurant)
        db.session.add_all(cls.tables)
        db.session.commit()

        cls.e = User(name='test manager', uname='testA1', password=User.hash_pw('123test123'), email='test@gmail.com', phone_number='123-456-7890',
            roles=[Role.query.filter_by(name='waitstaff').first()],
            groups=[Group.query.filter_by(name='employee').first()])
        
        db.session.add(cls.e)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        Restaurant.query.delete()
        Table.query.delete()
        Role.query.delete()
        Group.query.delete()
        Ingredient.query.delete()
        Intolerant.query.delete()
        User.query.delete()
        db.session.commit()
    
    def setUp(self):
        self.client = app.test_client()
        
        self.test_order = Order(employee_id=self.e.id, type='Takeout')
        db.session.add(self.test_order)
        db.session.commit()

    def test_get_login(self):
        """Test login_page displays properly"""
        resp = self.client.get('/login')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Login', html)

    def test_post_login(self):
        """Test that users can login"""

        # Incorrect user credentials
        with self.client.session_transaction() as session:
                session['restaurant_id'] = self.test_restaurant.id

        resp = self.client.post('/login', follow_redirects=True,
                                data={'username': self.e.uname, 
                                      'password': '123test'})
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn('User credentials incorrect, check username and password', html)

        # Correct user credentials
        resp = self.client.post('/login', follow_redirects=True,
                                data={'username': self.e.uname, 
                                      'password': '123test123'})
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'Welcome back {self.e.username}', html)
        # self.assertIsInstance(current_user, )

    def test_post_logout(self):
        resp = self.client.post('/logout', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Successfully logged out', html)

    def test_landing_page(self):
        """Test the landing page displays as expected"""
        resp = self.client.get('/')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("test restaurant", html)

    def test_get_assign_table_number(self):
        """Test assign table view"""
        resp = self.client.get('/dine-in/select-table')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Select Table', html)

    def test_post_assign_table_number(self):
        """Test assign table functionality"""
        with self.client:
            with self.client.session_transaction() as pre_session:
                pre_session['restaurant_id'] = self.test_restaurant.id

            resp = self.client.post('/dine-in/select-table', follow_redirects=True, data={"table_number": self.tables[0].id})
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Table assigned, enjoy your meal!", html)
            self.assertIsNotNone(session['current_order_id'])
            
            self.assertIsNotNone(session['curr_table_num'])
            curr_table = Table.query.filter_by(id=session['curr_table_num']).first()
            self.assertIsInstance(curr_table, Table)
            self.assertTrue(curr_table.taken)
