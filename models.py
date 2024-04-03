"""SQLAlchemy models for omakase"""

from flask_authorize import RestrictionsMixin, AllowancesMixin
from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# mapping tables
UserGroup = db.Table(
    'user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete="cascade")),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id', ondelete="cascade"))
)


UserRole = db.Table(
    'user_role', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete="cascade")),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete="cascade"))
)

##############Models#################

class Group(db.Model, RestrictionsMixin):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Role(db.Model, AllowancesMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

class Restaurant(db.Model):
    """Restaurant model
    There may be multiple restaurants owned by one entity
    """
    __tablename__ = 'restaurants'

    def __repr__(self):
        return f"<Restaurant #{self.id}, {self.name}>"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    phone_number = db.Column(db.String(20))
    description = db.Column(db.Text)

    menu = db.relationship('MenuItem', secondary="restaurants_menus", backref="restaurants")
    employees = db.relationship('User', backref='restaurant')

class User(db.Model, UserMixin):
    """User model:
    restaurant_id, name, address, birthday, role
    """
    __tablename__ = 'users'

    def __repr__(self):
        return f'<User #{self.id}, {self.username}, {self.groups[0].name}>'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, default='user')
    temp = db.Column(db.Boolean, nullable=False, default=False)
    uname = db.Column(db.String(255))
    password = db.Column(db.String(255))    
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id", ondelete="cascade"))
    email = db.Column(db.String(255))
    address = db.Column(db.String)
    birthday = db.Column(db.Date, default="1/1/1990")
    phone_number = db.Column(db.String(255))

    user_orders = db.relationship('Order', backref='employee')
    # `roles` and `groups` are reserved words that *must* be defined
    # on the `User` model to use group- or role-based authorization.
    roles = db.relationship('Role', secondary=UserRole)
    groups = db.relationship('Group', secondary=UserGroup)

    @hybrid_property
    def username(self):
        if self.uname is None:
            self.uname = self.name.replace(" ", "") + str(self.id)
            return self.uname
        else: 
            return self.uname

    @classmethod
    def hash_pw(cls, password):
        """Hash user's pasasword
        
        Hashes password
        """

        hashed_pwd = bcrypt.generate_password_hash(password)
        hashed_UTF8 = hashed_pwd.decode('utf-8')

        return hashed_UTF8

    @classmethod
    def Authenticate(cls, username, password):
        """authenticate user, return user object if all good"""
        user = User.query.filter(User.username==username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        
        return None

class CustomerOrder(db.Model):
    """Join table for customer-users to orders, in order to add 
    multiple customers to an order
    """
    __tablename__ = 'customers_orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="cascade"))
    
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
    
class Table(db.Model):
    """Table Model"""
    __tablename__ = 'tables'
    id = db.Column(db.Integer, primary_key=True)
    taken = db.Column(db.Boolean, nullable=False, default=False)

class Order(db.Model):
    """Order Model"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))

    table_number = db.Column(db.Integer, db.ForeignKey('tables.id', ondelete='cascade'))

    active = db.Column(db.Boolean, nullable=False, default=True)

    type = db.Column(db.String, nullable=False, default='Dining In')

    payment_method = db.Column(db.String)

    timestamp = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())

    customers = db.relationship('User', secondary="customers_orders", backref='order')
    
    ordered_items = db.relationship('OrderedItems', backref='associated_orders')

    @classmethod
    def serialize(cls, o):
        data = {
            "id": o.id,
            "table_number": o.table_number,
            "active": o.active,
            "type": o.type,
            "timestamp": o.timestamp,

            "ordered_items": [{'item_id':i.menu_item_id, 'qty':i.quantity} for i in o.ordered_items],
            }
        return data
    
    @hybrid_property
    def total_cost(self):
        total = 0
        for item in self.ordered_items:
            menu_item_cost = MenuItem.query.filter_by(id=item.menu_item_id).first().cost
            rate = item.quantity * menu_item_cost
            total += rate
        
        if self.type == 'Delivery':
            delivery_cost = 5
            total += delivery_cost
        return round(total, 2)
        
class OrderedItems(db.Model):
    """Join table for menu items that have been 
    ordered, and their associated order number. Default quantity is 0
    """
    __tablename__ = 'ordered_items'

    def __repr__(self):
        return f'<OrderedItem id:{self.id}, order_id:{self.order_id}, menu_item_id:{self.menu_item_id}, quantity: {self.quantity}>'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='cascade'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete='cascade'))
    quantity = db.Column(db.Integer, default=0)



    #########################################

def connect_db(app):
    """Connect this database to provided Flask app.
    
    This should be called in the Flask app
    """

    db.app = app
    db.init_app(app)