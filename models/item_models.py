"""Menu Item Models"""

from models.db import db
from models.restaurant_models import Restaurant
from sqlalchemy.exc import SQLAlchemyError

class MenuItem(db.Model):
    """Menu item model
    meal refers to what type it is: entree, appetizer, etc"""
    __tablename__ = 'menu_items'
    
    def __repr__(self):
        return f'<MenuItem {self.id}, {self.name}>'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image = db.Column(db.String, default='/static/images/food_placeholder.png')
    meal_type = db.Column(db.String)
    in_stock = db.Column(db.Boolean, nullable=False, default=True)
    vegetarian = db.Column(db.Boolean, nullable=False, default=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    ingredients = db.relationship('Ingredient', secondary='items_ingredients', backref='menu_items')
    intolerants = db.relationship('Intolerant', secondary='items_intolerants', backref='in_items')

    @classmethod
    def add_ingredients(cls, ingr_names_add, menu_item_id):
        """Add ingredient to a menu item
        ingr_names_add must be a list
        menu_item_id must be integer
        """

        all_ingredients = Ingredient.query.all()
        ingredient_names = [i.name for i in all_ingredients]
            
        # if ingredient in list of ingredients being added to new menu_item
        # not already in db, then add ingredient
        new_ingredients = []
        for i in ingr_names_add:
            if i and i not in ingredient_names:
                new_ingredients.append(Ingredient(name=i))

        db.session.add_all(new_ingredients)
        db.session.commit()

        # Get menu_item add_ingredients is called for and add ingredients to it
        menu_item = MenuItem.query.get_or_404(menu_item_id)
        filtered_ingredients = Ingredient.query.filter(Ingredient.name.in_(ingr_names_add))

        ingr_add = [i for i in filtered_ingredients]
        for i in ingr_add:
            menu_item.ingredients.append(i)

        db.session.commit()

        return menu_item

    @classmethod
    def add_intolerants(cls, int_names_add, menu_item_id):
        """Add intolerants to a menu item
        int_names_add must be a list
        """

        # If no intolerants being added, simply return
        if not int_names_add:
            return
        # This code is copied from above, but modified for intolerants
        # Consider data validation to check that intolerant exists in db
        menu_item = MenuItem.query.get_or_404(menu_item_id)
        filtered_intolerants = Intolerant.query.filter(Intolerant.name.in_(int_names_add))

        ingr_add = [i for i in filtered_intolerants]
        for i in ingr_add:
            menu_item.intolerants.append(i)

        db.session.commit()

        return menu_item
    
    @classmethod
    def add_new_item(cls, menu_item_form):
        restaurant = Restaurant.query.first()
        menu_item_data = { k:v for k, v in menu_item_form.items() if k != "csrf_token" and k != "intolerants" and k != 'ingredients' }
        
        menu_item = MenuItem(**menu_item_data)

        try:
            db.session.add(menu_item)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return None
        
        MenuItem.add_ingredients(menu_item_form["ingredients"], menu_item.id)
        MenuItem.add_intolerants(menu_item_form["intolerants"], menu_item.id)
        restaurant.menu.append(menu_item)

        try: 
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return None
        
        return menu_item

    @classmethod
    def serialize(cls, m):
        data = {
            "id": m.id,
            "name": m.name,
            "image": m.image,
            "meal_type": m.meal_type,
            "in_stock": m.in_stock,
            "vegetarian": m.vegetarian,
            "description": m.description,
            "cost": m.cost,
            "Ingredients": [i.name for i in m.ingredients],
            "Intolerants": [i.name for i in m.intolerants]
            }
        return data

class Ingredient(db.Model):
    """Ingredient model"""
    __tablename__ = 'ingredients'
    
    def __repr__(self):
        return f'<ingredient: {self.name}>'
        
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

class Intolerant(db.Model):
    """Intolerants aka food allergies model"""
    __tablename__ = 'intolerants'

    def __repr__(self):
        return f'<Intolerant: {self.name}>'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

class ItemIntolerant(db.Model):
    """Join table for MenuItem to Intolerant"""
    __tablename__ = 'items_intolerants'

    intolerant_id = db.Column(db.Integer, db.ForeignKey('intolerants.id', ondelete="cascade"), primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete="cascade"), primary_key=True)

class ItemIngredient(db.Model):
    """Join table for MenuItem to Ingredient"""
    __tablename__ = 'items_ingredients'

    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete="cascade"), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id', ondelete="cascade"), primary_key=True)

class RestaurantMenu(db.Model):
    """Join table for restaurants to menu_items

    the relationship b/w restaurants and menu items is many-many
    both ids set to primary key to keep combos unique
    """
    __tablename__ = 'restaurants_menus'

    menu_item_id = db.Column(db.ForeignKey('menu_items.id', ondelete='cascade'), primary_key=True)
    restaurant_id = db.Column(db.ForeignKey('restaurants.id', ondelete='cascade'), primary_key=True)
