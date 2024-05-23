"""Tests for item models"""

# Run tests like:
#
#   python -m unittest tests/test_models.py
# OR
#   python -m unittest tests.test_models.ItemModelTestCase.test_restaurant_model

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
from models.item_models import Ingredient, Intolerant, MenuItem

# We create our tables here once for all tests, then in each test we'll delete the data and create fresh new clean test data
db.drop_all()
db.create_all()
class MenuItemModelTestCase(TestCase):
    """Test the MenuItem Model"""

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

        db.session.add_all(cls.ingredients)
        db.session.add_all(cls.intolerants)
        db.session.add(cls.r)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        Restaurant.query.delete()
        MenuItem.query.delete()
        Ingredient.query.delete()
        Intolerant.query.delete()

        db.session.commit()
        
    def setUp(self):
        db.session.rollback()
        
        self.client = app.test_client()
    def test_menu_item(self):
        """Does basic MenuItem model work?"""
        
        mi = MenuItem(
                name = 'Spaghetti & Meatballs', 
                meal_type = 'Entree',
                description = 'Test Spaghetti & Meatballs',
                cost=13.95,
                ingredients=[Ingredient.query.filter_by(name='Pasta').first()],
                intolerants=[Intolerant.query.filter_by(name='Dairy').first()],
            )
        
        
        db.session.add(mi)
        db.session.commit()

        self.assertIsInstance(mi, MenuItem)
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
        mi_ingr_added = MenuItem.add_ingredients(['Test Ingredient'], mi.id)
        self.assertIsInstance(mi_ingr_added, MenuItem)

        # Test add_intolerants class method
        mi_int_added = MenuItem.add_intolerants(['Test Intolerant'], mi.id)
        self.assertIsInstance(mi_int_added, MenuItem)

        # Test serialize class method
        serial_mi = MenuItem.serialize(mi)
        self.assertIsInstance(serial_mi, dict)
        self.assertEqual(serial_mi['id'], mi.id)

    def test_ingredient(self):
        """Does basic ingredient model work?"""
        ingr = Ingredient(name='test ingredient 2')
        db.session.add(ingr)
        db.session.commit()

        self.assertIsInstance(ingr, Ingredient)

    def test_intolerant(self):
        """Does basic intolerant model work?"""
        intol = Intolerant(name='test intolerant')
        db.session.add(intol)
        db.session.commit()

        self.assertIsInstance(intol, Intolerant)
    