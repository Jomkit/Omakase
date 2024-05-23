"""Tests for user routes"""

# Run tests like:
#
#   python -m unittest tests/test_routes.py
# OR
#   python -m unittest tests.test_routes.BasicRoutesTestCase

import os
# from dotenv import load_env
# from flask import get_flashed_messages, session
from flask_login import login_user, logout_user
from psycopg2 import IntegrityError
from unittest import TestCase

# import models
from models.db import db
from models.restaurant_models import Restaurant
from models.user_models import Role, Group, User
from models.order_models import Order, Table
from models.item_models import Ingredient, Intolerant, MenuItem

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

class EmployeeTestCase(TestCase):
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
            roles=[Role.query.filter_by(name='manager').first()],
            groups=[Group.query.filter_by(name='employee').first()])
        
        self.e2 = User(name='test employee', uname='testE1', password=User.hash_pw('321test123'), email='test@gmail.com', phone_number='123-456-7890',
            roles=[Role.query.filter_by(name='waitstaff').first()],
            groups=[Group.query.filter_by(name='employee').first()])
        
        db.session.add_all([self.e, self.e2])
        db.session.commit()
        
        self.test_order = Order(employee_id=self.e.id, type='Takeout')
        db.session.add(self.test_order)
        db.session.commit()
        
        self.client = app.test_client()

    def tearDown(self): 
        User.query.delete()
        Order.query.delete()
        MenuItem.query.delete()
        db.session.commit()

    def test_get_add_employee_unauthorized(self):
        """Should not be able to access without manager privilege"""
        with app.test_request_context('/employees/add-employee'):
            logout_user()
            resp = self.client.get('/employees/add-employee')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 401)
            # self.assertRaises(IntegrityError)

    def test_get_add_employee(self):
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.get('/employees/add-employee')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add Employee', html)

    def test_post_add_employee(self):
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.post('/employees/add-employee', follow_redirects=True,
                                    data={
                                        'first_name': 'test',
                                        'last_name':'guy',
                                        'password': 'test123123',
                                        'roles': 'waitstaff',
                                        'email': 'test@gmail.com',
                                        'address': '1 Main St.',
                                        'phone_number': '123-456-7890'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('successfully added', html)

    def test_post_add_employee_phone_num_alt_format1(self):
        """/employees/add-employee accepts alternate format where area code surrounded by parenthesis ex: (123)456-7890
        """
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.post('/employees/add-employee', follow_redirects=True,
                                    data={
                                        'first_name': 'test',
                                        'last_name':'guy',
                                        'password': 'test123123',
                                        'roles': 'waitstaff',
                                        'email': 'test@gmail.com',
                                        'address': '1 Main St.',
                                        'phone_number': '(123)456-7890'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('successfully added', html)

    def test_post_add_employee_phone_num_alt_format2(self):
        """/employees/add-employee accepts 10 digit phone number with no punctuation
            ex: 1234567890
        """
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.post('/employees/add-employee', follow_redirects=True,
                                    data={
                                        'first_name': 'test',
                                        'last_name':'guy',
                                        'password': 'test123123',
                                        'roles': 'waitstaff',
                                        'email': 'test@gmail.com',
                                        'address': '1 Main St.',
                                        'phone_number': '1234567890'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('successfully added', html)

    def test_post_add_employee_country_code_fail(self):
        """Adding employee should fail if including country code"""
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
                                        'phone_number': '`+1(123)456-7890'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid input.', html)

    def test_post_add_employee_password_short(self):
        """Adding employee should fail if the password is less than 8 characters"""
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
                                        'phone_number': '123-456-7890'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Field must be at least 8 characters long.', html)

    def test_post_add_employee_phone_num_too_short(self):
        """Adding employee should fail if the phone number is less than 10 characters"""
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.post('/employees/add-employee', follow_redirects=True,
                                    data={
                                        'first_name': 'test',
                                        'last_name':'guy',
                                        'password': 'test123123',
                                        'roles': 'waitstaff',
                                        'email': 'test@gmail.com',
                                        'address': '1 Main St.',
                                        'phone_number': '123-456'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Field must be between 10 and 14 characters long.', html)

    def test_post_add_employee_phone_num_too_long(self):
        """Adding employee should fail if the phone number is more than 14 characters"""
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.post('/employees/add-employee', follow_redirects=True,
                                    data={
                                        'first_name': 'test',
                                        'last_name':'guy',
                                        'password': 'test123123',
                                        'roles': 'waitstaff',
                                        'email': 'test@gmail.com',
                                        'address': '1 Main St.',
                                        'phone_number': '123-4560000000'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid input.', html)

    def test_post_add_employee_phone_num_incorrect_format(self):
        """Adding employee should fail if the phone number has incorrect format.
        Accepted formats: 
            1234567890
            123-456-7890
            (123)456-7890
        """
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.post('/employees/add-employee', follow_redirects=True,
                                    data={
                                        'first_name': 'test',
                                        'last_name':'guy',
                                        'password': 'test123123',
                                        'roles': 'waitstaff',
                                        'email': 'test@gmail.com',
                                        'address': '1 Main St.',
                                        'phone_number': 'asdf456-7890'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid input.', html)

    def test_post_add_employee_invalid_email(self):
        """Adding employee should fail if email does not follow proper format"""
        with app.test_request_context('/employees/add-employee'):
            login_user(self.e)
            
            resp = self.client.post('/employees/add-employee', follow_redirects=True,
                                    data={
                                        'first_name': 'test',
                                        'last_name':'guy',
                                        'password': 'test123123',
                                        'roles': 'waitstaff',
                                        'email': 'testgmailscom',
                                        'address': '1 Main St.',
                                        'phone_number': '123-456-7890'
                                    })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid email address.', html)

    def test_show_employee_list(self):
        with app.test_request_context('/employees/list'):
            login_user(self.e)

            resp = self.client.get('/employees/list')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Employee List', html)
            self.assertIn('test manager', html)

    def test_show_employee_dashboard(self):
        with app.test_request_context('/employees/employee-dashboard'):
            login_user(self.e)

            with self.client.session_transaction() as session:
                session['restaurant_id'] = self.test_restaurant.id     

            resp = self.client.get('/employees/employee-dashboard')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Employee Dashboard', html)
            self.assertIn(f'Order #{self.test_order.id}', html)

    def test_delete_employee(self):
        """DELETE /employees/<id>/delete
        
        successfully deletes an employee

        authorization: manager
        """
        with app.test_request_context('/employees/list'):
            login_user(self.e)
            deleted_id = self.e2.id

            resp = self.client.post(f"/employees/{self.e2.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"Deleted user {deleted_id}", html)

    def test_delete_employee_not_self(self):
        """Managers can't delete themselves. 
        This is to prevent losing access to manager privileges
        """
        with app.test_request_context('/employees/list'):
            logout_user
            login_user(self.e)

            resp = self.client.post(f"/employees/{self.e.id}/delete", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 401)

    def test_delete_employee_unauthorized(self):
        """Delete employee unsuccessful without manager auth
        """
        with app.test_request_context('/employees/list'):
            login_user(self.e2)
            resp = self.client.post(f"/employees/{self.e.id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 401)

    def test_delete_employee_not_found(self):
        """Delete employee unsuccessful without manager auth
        """        
        with app.test_request_context('/employees/list'):
            login_user(self.e)
            resp = self.client.post(f"/employees/999/delete", follow_redirects=True)
           
            self.assertEqual(resp.status_code, 404)

    def test_get_add_menu(self):
        with app.test_request_context('/employees/add-menu-item'):
            login_user(self.e)

            resp = self.client.get('/employees/add-menu-item')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add Menu Item', html)

    def post_add_menu_item(self):
        with app.test_request_context('/employees/add-menu-item'):
            login_user(self.e)

            resp = self.client.post('/employees/add-menu-item', follow_redirects=True, 
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

    def post_add_menu_with_image(self):
        """/employees/add-menu-item accepts image url if properly formatted"""
        with app.test_request_context('/employees/add-menu-item'):
            login_user(self.e)

            resp = self.client.post('/employees/add-menu-item', follow_redirects=True, 
                                    data={
                                        'name': 'test item',
                                        'image': 'https://images.pexels.com/photos/793785/pexels-photo-793785.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
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

    def post_add_menu_invalid_url(self):
        with app.test_request_context('/employees/add-menu-item'):
            login_user(self.e)

            resp = self.client.post('/employees/add-menu-item', follow_redirects=True, 
                                    data={
                                        'name': 'test item',
                                        'image': 'eorivnaweo34w8w',
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
            self.assertIn('Invalid URL.', html)

    def get_edit_restaurant(self):
        """Show edit restaurant form"""
        with app.test_request_context('/employees/edit-restaurant'):
            with self.client.session_transaction() as session:
                session['restaurant_id'] = self.test_restaurant.id

            login_user(self.e)

            resp = self.client.get('/employees/edit-restaurant')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200) 
            self.assertIn('Edit Restaurant Information', html)

    def post_edit_restaurant(self):
        """Successfully updates restaurant info"""
        with app.test_request_context('/employees/edit-restaurant'):
            with self.client.session_transaction() as session: 
                session['restaurant_id'] = self.test_restaurant.id
            login_user(self.e)

            test_name = 'New Test Restaurant'

            resp = self.client.post('/employees/edit-restaurant', follow_redirects=True, data={
                'name': test_name
            })
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(test_name, html)

    # def post_edit_restaurant_empty_field(self):
    #     """Empty field triggers invalid input message from form"""
    #     with app.test_request_context('/employees/edit-restaurant'):
    #         with self.client.session_transaction() as session: 
    #             session['restaurant_id'] = self.test_restaurant.id
    #         login_user(self.e)
            
    #         resp = self.client.post('/employees/edit-restaurant', follow_redirects=True, data={
    #             'name': None
    #         })
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('This field is required', html)

