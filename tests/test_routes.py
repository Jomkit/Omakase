"""Tests for the routes"""

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

class BasicRoutesTestCase(TestCase):
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

        cls.e = models.User(name='test admin', uname='testA1', password=models.User.hash_pw('123test123'), email='test@gmail.com', phone_number='123-456-7890',
            roles=[models.Role.query.filter_by(name='waitstaff').first()],
            groups=[models.Group.query.filter_by(name='employee').first()])
        
        db.session.add(cls.e)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        db = models.db
        models.Restaurant.query.delete()
        models.Table.query.delete()
        # models.Role.query.delete()
        # models.Group.query.delete()
        models.Ingredient.query.delete()
        models.Intolerant.query.delete()
        models.User.query.delete()
        db.session.commit()
    
    def setUp(self):
        self.client = app.test_client()

    def test_get_login(self):
        """Test login_page displays properly"""
        resp = self.client.get('/login')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Login', html)

    def test_post_login(self):
        """Test that users can login"""

        # Incorrect user credentials
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

            resp = self.client.post('/dine-in/select-table', follow_redirects=True, data={"table_number": self.tables[0].id})
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Table assigned, enjoy your meal!", html)
            self.assertIsNotNone(session['current_order_id'])
            
            self.assertIsNotNone(session['current_table'])
            curr_table = models.Table.query.filter_by(id=session['current_table']).first()
            self.assertIsInstance(curr_table, models.Table)
            self.assertTrue(curr_table.taken)

class OrderTestCase(TestCase):
    @classmethod 
    def setUpClass(cls):
        db = models.db

        cls.test_restaurant = models.Restaurant(name='test restaurant', address='1 Test St.')

        cls.tables = [
            models.Table(),
            models.Table(),
        ]

        # cls.roles = [
        #     models.Role(name='waitstaff'),
        #     models.Role(name='kitchen'),
        #     models.Role(name='admin'),
        # ]
        
        # cls.groups = [
        #     models.Group(name='employee'),
        #     models.Group(name='customer'),
        # ]

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
        
        # db.session.add_all(cls.roles)
        # db.session.add_all(cls.groups)
        db.session.add(cls.test_restaurant)
        db.session.add_all(cls.tables)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db = models.db
        models.Restaurant.query.delete()
        models.Table.query.delete()
        # models.Role.query.delete()
        # models.Group.query.delete()
        models.Ingredient.query.delete()
        models.Intolerant.query.delete()
        models.User.query.delete()
        db.session.commit()
    
    def setUp(self):
        self.e = models.User(name='test admin', uname='testA1', password=models.User.hash_pw('123test123'), email='test@gmail.com', phone_number='123-456-7890',
            roles=[models.Role.query.filter_by(name='waitstaff').first()],
            groups=[models.Group.query.filter_by(name='employee').first()])
        
        models.db.session.add(self.e)
        models.db.session.commit()
        
        self.test_order = models.Order(employee_id=self.e.id, type='Takeout')
        models.db.session.add(self.test_order)
        models.db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        models.User.query.delete()
        models.Order.query.delete()
        models.db.session.commit()
                       
    def test_show_order_page(self):
        with self.client.session_transaction() as session:
                session['current_order_id'] = self.test_order.id

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
            resp = self.client.post('/takeout/contact-form', follow_redirects=True,
                                    data={
                                        'contact_info-name': 'test customer',
                                        'contact_info-phone_number': '123-456-7890'
                                    })
            html = resp.get_data(as_text=True)
            testUser = models.User.query.filter_by(name="test customer").first()

            self.assertEqual(resp.status_code, 200)
            self.assertIn("We&#39;re pleased to take your order, test customer!", html)
            self.assertIn("Menu", html)

            self.assertIsInstance(session['current_order_id'], int)
            self.assertEqual(testUser.name, 'test customer')
            self.assertTrue(testUser.temp)
            self.assertEqual('customer', testUser.groups[0].name)

            test_order = models.Order.query.filter_by(id=session['current_order_id']).first()
            self.assertEqual(test_order.type, 'Takeout')

    def test_get_delivery_contact_form(self):
        resp = self.client.get('/delivery/contact-form')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Delivery', html)

    def test_post_delivery_contact_form(self):
        with self.client:
            resp = self.client.post('/delivery/contact-form', follow_redirects=True,
                                    data={
                                        'contact_info-name': 'test customer',
                                        'contact_info-phone_number': '123-456-7890',
                                        'address-street': '123 Test St', 
                                        'address-city':'Test City',
                                        'address-state':'New York'
                                    })
            html = resp.get_data(as_text=True)
            testUser = models.User.query.filter_by(name="test customer").first()

            self.assertEqual(resp.status_code, 200)
            self.assertIn("We&#39;re pleased to take your order, test customer!", html)
            self.assertIn("Menu", html)

            self.assertIsInstance(session['current_order_id'], int)
            self.assertEqual(testUser.name, 'test customer')
            self.assertEqual(testUser.address, '123 Test St, Test City, New York')
            self.assertTrue(testUser.temp)
            self.assertEqual('customer', testUser.groups[0].name)

            test_order = models.Order.query.filter_by(id=session['current_order_id']).first()
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

class EmployeeTestCase(TestCase):
    @classmethod 
    def setUpClass(cls):
        db = models.db

        cls.test_restaurant = models.Restaurant(name='test restaurant', address='1 Test St.')

        cls.tables = [
            models.Table(),
            models.Table(),
        ]

        # cls.roles = [
        #     models.Role(name='waitstaff'),
        #     models.Role(name='kitchen'),
        #     models.Role(name='admin'),
        # ]
        
        # cls.groups = [
        #     models.Group(name='employee'),
        #     models.Group(name='customer'),
        # ]

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
        
        # db.session.add_all(cls.roles)
        # db.session.add_all(cls.groups)
        db.session.add(cls.test_restaurant)
        db.session.add_all(cls.tables)
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db = models.db
        models.Restaurant.query.delete()
        models.Table.query.delete()
        # models.Role.query.delete()
        # models.Group.query.delete()
        models.Ingredient.query.delete()
        models.Intolerant.query.delete()
        models.User.query.delete()
        db.session.commit()
    
    def setUp(self):
        self.e = models.User(name='test admin', uname='testA1', password=models.User.hash_pw('123test123'), email='test@gmail.com', phone_number='123-456-7890',
            roles=[models.Role.query.filter_by(name='admin').first()],
            groups=[models.Group.query.filter_by(name='employee').first()])
        
        models.db.session.add(self.e)
        models.db.session.commit()
        
        self.test_order = models.Order(employee_id=self.e.id, type='Takeout')
        models.db.session.add(self.test_order)
        models.db.session.commit()
        
        self.client = app.test_client()

    def tearDown(self):
        models.User.query.delete()
        models.Order.query.delete()
        models.MenuItem.query.delete()
        models.db.session.commit()

    def test_get_add_employee_unauthorized(self):
        """Should not be able to access without admin priviledge"""
        with app.test_request_context('/employees/add-employee'):
            logout_user()
            resp = self.client.get('/employees/add-employee')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 401)
            self.assertIn("unauthorized", html)

    def test_get_add_employee(self):
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.get('/employees/add-employee')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign Up', html)

    def test_post_add_employee(self):
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.post('/employees/add-employee', follow_redirects=True,
                                    data={
                                        'first_name': 'test',
                                        'last_name':'guy',
                                        'password': 'test123',
                                        'roles': 'waitstaff',
                                        'email': 'test@gmail.com',
                                        'address': '1 Main St.',
                                        'birthday': '1/1/1996',
                                        'phone_number': '123-456-7890'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('successfully added', html)

    def test_show_employee_list(self):
        with app.test_request_context('/employees/list'):
            login_user(self.e)

            resp = self.client.get('/employees/list')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Employee List', html)
            self.assertIn('test admin', html)

    def test_show_employee_dashboard(self):
        with app.test_request_context('/employee-dashboard'):
            login_user(self.e)

            resp = self.client.get('/employee-dashboard')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Employee Dashboard', html)
            self.assertIn(f'Order #{self.test_order.id}', html)

    def test_get_add_menu(self):
        with app.test_request_context('/add-menu-item'):
            login_user(self.e)

            resp = self.client.get('/add-menu-item')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add Menu Item', html)

    def post_add_menu(self):
        with app.test_request_context('/add-menu-item'):
            login_user(self.e)

            resp = self.client.post('/add-menu-item', follow_redirects=True, 
                                    data={
                                        'name': 'test item',
                                        'meal_type': 'entree',
                                        'in_stock': True,
                                        'vegetarian': False,
                                        'description': 'Test menu item description',
                                        'cost': 4.95,
                                        'ingredients': 'Carrot',
                                        'intolerants': 'Dairy'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Added test item!', html)
