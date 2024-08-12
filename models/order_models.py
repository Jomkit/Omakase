"""SQLAlchemy models for omakase"""

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from models.db import db
from models.item_models import MenuItem
from models.restaurant_models import Table

class Order(db.Model):
    """Order Model"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))

    table_number = db.Column(db.Integer, db.ForeignKey('tables.id', ondelete='cascade'))

    active = db.Column(db.Boolean, nullable=False, default=True)

    need_assistance = db.Column(db.Boolean, nullable=False, default=False)

    type = db.Column(db.String, nullable=False, default='Dining In')

    payment_method = db.Column(db.String)

    timestamp = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())

    customers = db.relationship('User', secondary="customers_orders", backref='order')
    
    ordered_items = db.relationship('OrderedItems', backref='associated_orders')

    @classmethod
    def create(cls, table_number=None, type='Dining In'):

        new_order = Order(table_number=table_number, type=type)
        try:
            db.session.add(new_order)
            db.session.commit() 
        except SQLAlchemyError as e:
            db.session.rollback()
            print("An error occurred while creating a new order:", e)
        return new_order
    
        """
        This class method is used to serialize an Order object into a dictionary format for use in JSON.
        It takes an Order object as a parameter and returns a dictionary containing the order's details.

        The ordered items are represented as a list of dictionaries, each containing the item's id and quantity.
        """
    @classmethod
    def serialize(cls, o):
        data = {
            "id": o.id,
            "table_number": o.table_number,
            "active": o.active,
            "need_assistance": o.need_assistance,
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

    def set_payment_method(self, payment_method):
        self.payment_method = payment_method
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print("An error occurred while setting payment method:", e)
    

    def update(self, data):
        for k,v in data.items():
            setattr(self, k, v)
        
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print("An error occurred while updating order:", e)

    def close(self):
        """Closes order"""
        self.active = False
        self.table_number = None
        
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print("An error occurred while closing order:", e)
        
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

    @classmethod
    def get_or_create_ordered_item(cls, order, menu_item_id):
        """Gets or creates an OrderedItem object for the given order_id and menu_item_id"""
        
        # Query ordered_item by order id and menu_item_id
        ordered_item = OrderedItems.query.filter(OrderedItems.order_id==order.id, OrderedItems.menu_item_id == menu_item_id).first()

        # if menu_item was not on the order, ordered_item will be falsey. Instantiate (default qty=0)
        if not ordered_item:
            ordered_item = OrderedItems(menu_item_id=menu_item_id)
            order.ordered_items.append(ordered_item)

            try:
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                print("An error occurred while creating an ordered item:", e)

        return ordered_item
    
    def update(self, data):
        """Update the OrderedItem object with the given data object"""
        for k,v in data.items():
            setattr(self, k, v)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print("An error occurred while updating an ordered item:", e)
        
        
class CustomerOrder(db.Model):
    """Join table for customer-users to orders, in order to add 
    multiple customers to an order
    """
    __tablename__ = 'customers_orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="cascade"))