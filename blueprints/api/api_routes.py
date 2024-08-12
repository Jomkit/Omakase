############ Omakase API  Blueprint############
from flask import Blueprint, jsonify, request
from models.item_models import MenuItem
from models.order_models import Order, OrderedItems
from models.db import db

api_bp = Blueprint('api', __name__)

##########ORDER API##############
@api_bp.route('/orders')
def get_all_orders():
    """Get all order objects and return jsonified"""
    all_orders = Order.query.all()
    data = []

    for order in all_orders:
        data.append(Order.serialize(order))

    return(jsonify(data=data), 200)

@api_bp.route('/order/<int:id>')
def get_order(id):
    """get an order object and return jsonified order object"""
    order = Order.query.get_or_404(id)

    data = Order.serialize(order)
    return (jsonify(data=data), 200)

@api_bp.route('/order', methods=['POST'])
def new_order():
    """Create new order"""
    new_order = Order.create(**request.json)
    data = Order.serialize(new_order)
    return (jsonify(data=data), 200)

@api_bp.route('/order/<int:id>', methods=['PATCH'])
def update_order(id):
    """Update existing orders"""
    order = Order.query.get_or_404(id)
    order.update(request.json.get('data'))

    data = Order.serialize(order)

    return (jsonify(data=data), 200)

@api_bp.route('/order/<int:id>/add_item', methods=['PATCH'])
def add_to_order(id):
    """Add a menu item from id with qty=1 to an existing order"""
    
    order = Order.query.get_or_404(id)
    menu_item_id = request.json.get('menu_item_id')  
    ordered_item = OrderedItems.get_or_create_ordered_item(order, menu_item_id)
    
    ordered_item.update({'quantity': ordered_item.quantity + 1})
    data = Order.serialize(order)

    return (jsonify(updated_order=data), 202)

##############MENU API##################
@api_bp.route('/menu/<int:id>')
def get_menu_item(id):
    menu_item = MenuItem.query.get_or_404(id)

    data = MenuItem.serialize(menu_item)
    
    return (jsonify(data=data), 200)

@api_bp.route('/menu/list_menu_items')
def list_menu_items():
    items = MenuItem.query.all()
    results = [MenuItem.serialize(item) for item in items]

    return (jsonify(data=results), 200)
