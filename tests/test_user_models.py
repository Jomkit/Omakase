"""Tests for the models"""

# Run tests like:
#
#   python -m unittest tests/test_models.py
# OR
#   python -m unittest tests.test_models.RestaurantModelTestCase.test_restaurant_model

import os
from unittest import TestCase

from datetime import date
# Before importing app, set environmental variable to use a test db for tests

os.environ['DATABASE_URL'] = 'postgresql:///omakase-test'

# now import app

import datetime
from app import app
from models.db import db
from models.restaurant_models import Restaurant
from models.user_models import User, Role, Group
from models.item_models import Ingredient, Intolerant, MenuItem

# We create our tables here once for all tests, then in each test we'll delete the data and create fresh new clean test data
db.drop_all()
db.create_all()

class RestaurantModelTestCase(TestCase):
    """Test the Restaurant Model"""

    @classmethod
    def setUpClass(cls):
        """Set up test data at beginning of TestCase"""

        cls.r = Restaurant(
            name = 'Test Restaurant',
            address = '123 Main Street', 
            phone_number = '123-456-7890'
        )

        db.session.add(cls.r)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        Restaurant.query.delete()
        db.session.commit()
        
    def setUp(self):
        """Create test client, and add sample restaurant"""
        db.session.rollback()
        User.query.delete()

        self.e = User(restaurant_id=self.r.id, name='Test', password=User.hash_pw('testpassword123'), address='1 Test Rd', birthday='1/1/1990', roles=[])

        db.session.add(self.e)
        db.session.commit()

    def test_restaurant_model(self):
        """Does the basic restaurant model work?"""

        r = self.r
        
        self.assertIsInstance(r, Restaurant)       
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

        cls.r = Restaurant(
            name = 'Test Restaurant',
            address = '123 Main Street', 
            phone_number = '123-456-7890'
        )
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
        db.session.add(cls.r)
        db.session.commit()
        
    @classmethod
    def tearDownClass(cls):
        Restaurant.query.delete()
        User.query.delete()
        MenuItem.query.delete()
        Role.query.delete()
        Group.query.delete()
        Ingredient.query.delete()
        Intolerant.query.delete()
        
        db.session.commit()
        
    def setUp(self):
        """Create test client, and add sample restaurant"""
        db.session.rollback()
        User.query.delete()

        self.e = User(restaurant_id=db.session.query(Restaurant.id).first(), password=User.hash_pw('testpassword123'), name='Test', address='1 Test Rd', birthday='1/1/1990',
            roles=[Role.query.filter_by(name='waitstaff').first()],
            groups=[Group.query.filter_by(name='employee').first()])



        self.test_manager = User(restaurant_id=db.session.query(Restaurant.id).first(), password=User.hash_pw('test123password123'), name='Test', address='1 Test Rd', birthday='1/1/1990',
            roles=[Role.query.filter_by(name='manager').first()],
            groups=[Group.query.filter_by(name='employee').first()])

        db.session.add(self.e)
        db.session.commit()

    def test_user_model(self):
        """Does the basic User model work?"""

        e = User(restaurant_id=db.session.query(Restaurant.id).first(), name='Test Guy', address='12 Test Rd', birthday='2/2/1990', password=User.hash_pw('123test123'), email='test@gmail.com', phone_number='123-456-7890',
        roles=[Role.query.filter_by(name='waitstaff').first()],
        groups=[Group.query.filter_by(name='employee').first()]
        )
        db.session.add(e)
        db.session.commit()

        self.assertIsInstance(e, User)
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

        self.assertNotEqual('testpw123', User.hash_pw('testpw123'))
        self.assertIsInstance(User.Authenticate(e.uname, '123test123'), User)

    def test_register_employee(self):

        # Prepare test employee data
        employee_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'testpassword',
            'roles': 'manager',
            'email': 'john.doe@example.com',
            'address': '123 Main St',
            'birthday': '1990-01-01',
            'phone_number': '123-555-1234'
        }

        # Call the register_employee method
        new_employee = User.register_employee(employee_data)

        # Assert that the new employee was created correctly
        self.assertIsNotNone(new_employee)
        self.assertEqual(new_employee.name, 'John Doe')
        self.assertTrue(User.Authenticate(new_employee.username, employee_data['password']))
        self.assertEqual(new_employee.email, 'john.doe@example.com')
        self.assertEqual(new_employee.address, '123 Main St')
        self.assertEqual(new_employee.birthday, datetime.date(1990, 1, 1))
        self.assertEqual(new_employee.phone_number, '123-555-1234')
        self.assertEqual('manager', new_employee.roles[0].name)
        self.assertEqual("employee", new_employee.groups[0].name)

    def test_register_customer(self):
        # Prepare test customer data
        customer_data = {
            "contact_info": {
                "name": "Jane Smith",
                "phone_number": "123-555-5678"
            },
            "address": {
                "street": "456 Oak Rd",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345"
            }
        }

        # Call the register_customer method
        new_customer = User.register_customer(customer_data)

        # Assert that the new customer was created correctly
        self.assertIsNotNone(new_customer)
        self.assertEqual(new_customer.name, "Jane Smith")
        self.assertEqual(new_customer.phone_number, "123-555-5678")
        self.assertEqual(new_customer.address, "456 Oak Rd, Anytown, CA, 12345")
        self.assertTrue(new_customer.temp)
        self.assertIn(Group.query.filter_by(name='customer').first(), new_customer.groups)
    def test_register_customer_partial(self):
        # Prepare test customer data
        customer_data = {
            "contact_info": {
                "name": "Jane Smith",
                "phone_number": "123-555-5678"
            },
            # "address": {
            #     "street": "456 Oak Rd",
            #     "city": "Anytown",
            #     "state": "CA",
            #     "zip_code": "12345"
            # }
        }

        # Call the register_customer method
        new_customer = User.register_customer(customer_data)

        # Assert that the new customer was created correctly
        self.assertIsNotNone(new_customer)
        self.assertEqual(new_customer.name, "Jane Smith")
        self.assertEqual(new_customer.phone_number, "123-555-5678")
        self.assertTrue(new_customer.temp)
        self.assertIn(Group.query.filter_by(name='customer').first(), new_customer.groups)

    def test_delete_user(self):
        test_employee = self.e

        self.assertIsInstance(test_employee, User)
        User.delete(test_employee.id)
        res = User.query.filter_by(id=test_employee.id).first()
        print(res)
        self.assertIsNone(res)
        