"""Tests for restaurant model and related"""

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
from models.restaurant_models import Restaurant, Table

db.drop_all()
db.create_all()
class RestaurantModelTestCase(TestCase):
    """Test the Restaurant Model"""
        
    def setUp(self):
        db.session.rollback()
        
        self.r = Restaurant(
            name = 'Test Restaurant',
            address = '123 Main Street', 
            phone_number = '123-456-7890',
            description = 'Hello yes this is a description beep boop restaurant stuff'
        )

        db.session.add(self.r)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        Restaurant.query.delete()

    def test_restaurant(self):
        """Does the basic restaurant model work?"""
        r1 = Restaurant(
            name = 'Test Restaurant 2',
            address = '321 Alphabet Street',
            phone_number = '098-765-4321',
            description = 'Second test restaurant opened in 1990'
        )

        self.assertIsInstance(r1, Restaurant)

    def test_update_restaurant(self):
        """Restaurant's update instance method should take at least one parameter and up to all that the restaurant has and update the corresponding ones"""
        restaurant_data = {
            'name': "New Test Restaurant"
        }

        self.assertEqual(self.r.name, "Test Restaurant")
        self.r.update(restaurant_data)
        self.assertEqual(self.r.name, restaurant_data['name'])
