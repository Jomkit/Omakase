"""Tests for user routes"""

# Run tests like:
#
#   python -m unittest tests/test_routes.py
# OR
#   python -m unittest tests.test_routes.BasicRoutesTestCase

import os
# from dotenv import load_env
from flask import session
from unittest import TestCase

# import models
from models.db import db
from models.restaurant_models import Restaurant
from models.user_models import Role, Group, User
from models.order_models import Order, Table
from models.item_models import Ingredient, Intolerant

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
db.drop_all()
db.create_all()

class OrderTestCase(TestCase):
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
        self.e = User(name='test manager', uname='testA1', password=User.hash_pw('123test123'), email='test@gmail.com', phone_number='123-456-7890',
            roles=[Role.query.filter_by(name='waitstaff').first()],
            groups=[Group.query.filter_by(name='employee').first()])
        
        db.session.add(self.e)
        db.session.commit()
        
        self.test_order = Order(employee_id=self.e.id, type='Takeout')
        db.session.add(self.test_order)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        User.query.delete()
        Order.query.delete()
        db.session.commit()
                       
    def test_show_order_page(self):
        with self.client.session_transaction() as session:
                session['current_order_id'] = self.test_order.id
                session['restaurant_id'] = self.test_restaurant.id

        resp = self.client.get('/order')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Itemized Bill', html)
        self.assertIn('Menu', html)

    def test_takeout_route(self):
        resp = self.client.get('/takeout')

        # Check redirect
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "/takeout/contact-form")

    def test_delivery_route(self):
        resp = self.client.get('/delivery')

        # Check redirect
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "/delivery/contact-form")

    def test_get_takeout_contact_form(self):
        resp = self.client.get('/takeout/contact-form')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Takeout', html)
    
    def test_post_takeout_contact_form(self):
        with self.client:
            with self.client.session_transaction() as pre_session:
                # session['current_order_id'] = self.test_order.id
                pre_session['restaurant_id'] = self.test_restaurant.id
            
            postUser = {"name": "test customer", "phone_number": "123-456-7890"}
            resp = self.client.post('/takeout/contact-form', follow_redirects=True,
                                    data={
                                        "contact_info-name": postUser['name'],
                                        "contact_info-phone_number": postUser['phone_number']
                                    })
            html = resp.get_data(as_text=True)
            testUser = User.query.filter_by(name="test customer").first()

            self.assertEqual(resp.status_code, 200)
            self.assertIn("We&#39;re pleased to take your order, test customer!", html)
            self.assertIn("Menu", html)

            self.assertIsInstance(session['current_order_id'], int)
            self.assertEqual(testUser.name, postUser['name'])
            self.assertTrue(testUser.temp)
            self.assertEqual('customer', testUser.groups[0].name)

            test_order = Order.query.filter_by(id=session['current_order_id']).first()
            self.assertEqual(test_order.type, 'Takeout')

    def test_get_delivery_contact_form(self):
        resp = self.client.get('/delivery/contact-form')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Delivery', html)

    def test_post_delivery_contact_form(self):
        with app.test_request_context('/delivery/contact-form'):
            with self.client:
                with self.client.session_transaction() as pre_session:
                    pre_session['restaurant_id'] = self.test_restaurant.id

                resp = self.client.post('/delivery/contact-form', follow_redirects=True,
                                        data={
                                            "contact_info-name": "test customer", 
                                            "contact_info-phone_number": "123-456-7890",
                                            "address-street": "123 Test St", 
                                            "address-city": "Test City", 
                                            "address-state": "New York"
                                        
                                        })
                html = resp.get_data(as_text=True)
                testUser = User.query.filter_by(name="test customer").first()

                self.assertEqual(resp.status_code, 200)
                self.assertIn("We&#39;re pleased to take your order, test customer!", html)
                self.assertIn("Menu", html)

                self.assertIsInstance(session['current_order_id'], int)
                self.assertEqual(testUser.name, 'test customer')
                self.assertEqual(testUser.address, '123 Test St, Test City, New York')
                self.assertTrue(testUser.temp)
                self.assertEqual('customer', testUser.groups[0].name)

                test_order = Order.query.filter_by(id=session['current_order_id']).first()
                self.assertEqual(test_order.type, 'Delivery')

    def test_show_checkout_page(self):
        with self.client.session_transaction() as session:
                session['current_order_id'] = self.test_order.id
                
        resp = self.client.get('/checkout')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Checkout', html)
        self.assertIn('Final Bill', html)

    def test_get_payment(self):
        resp = self.client.get('/payment')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Payment', html)
        self.assertIn('Choose Your Payment Method', html)

    def test_post_payment(self):
        with self.client:
            with self.client.session_transaction() as session:
                session['current_order_id'] = self.test_order.id
            
            resp = self.client.post('/payment', follow_redirects=True, data={"payment_method":"cash"})
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(session['current_order_id'], self.test_order.id)
            self.assertEqual(self.test_order.payment_method, "cash")
            self.assertIn('Thank you for your patronage!', html)

    def test_show_thank_you_page(self):
        with self.client:
            with self.client.session_transaction() as session:
                session['current_order_id'] = self.test_order.id        
        
            resp = self.client.get('/thank_you')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Thank you for your patronage!", html)

            self.assertFalse(self.test_order.active)
            self.assertIsNone(self.test_order.table_number)
