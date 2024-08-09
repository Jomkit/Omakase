########## Customer Routes Blueprint ############

import pdb
from functools import wraps
from flask import Blueprint, render_template, redirect, flash, session, url_for, current_app, request
from models.db import db
from models.user_models import User, Group
from models.restaurant_models import Restaurant, Table
from models.order_models import Order
from forms import SelectTableForm, TakeoutForm, DeliveryForm, PaymentMethodForm
from flask_authorize import Authorize

authorize = Authorize(current_app)
customers_bp = Blueprint('customers', __name__, template_folder='templates')

############# Custom Decorators ##############
def order_active(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('current_order_id'):

            return redirect(url_for('customers.order_page'))
        return f(*args, **kwargs)
    return decorated_function

# Redirect to dashboard if logged in as employee
def employee_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if(authorize.in_group('employee')):
            return redirect(url_for('employees.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
##############################################

@customers_bp.route('/')
@employee_redirect
def landing_page():
    
    restaurant = db.session.query(Restaurant).first()
    session['restaurant_id'] = restaurant.id
    return render_template('landing.html', restaurant=restaurant)

# @app.route('/signup')

@customers_bp.route('/dine-in/select-table', methods=['GET', 'POST'])
@order_active # if there's a current order, skip to order page
@employee_redirect
def assign_table_number():
    """Set up new Order instance and assign table_number, for dining in"""
        
    form = SelectTableForm()
    tables = [(table.id, table.id) for table in Table.query.all() if not table.taken]
    form.table_number.choices = tables
    
    if form.validate_on_submit():
        Table.assign(form.table_number.data)
        new_order = Order.create(form.table_number.data, 'Dining In')

        session['current_order_id'] = new_order.id
        session['curr_table_num'] = new_order.table_number

        flash('Table assigned, enjoy your meal!', 'success')
        return redirect(url_for('customers.order_page'))

    return render_template('select-table-form.html', form=form)

@customers_bp.route('/order')
@employee_redirect
def order_page():
    """Display order page with menu and updating itemized bill on the side"""
    restaurant = db.session.query(Restaurant).filter_by(id=session['restaurant_id']).first()
    meal_types = {item.meal_type for item in restaurant.menu}
    curr_order_type = db.session.query(Order.type).filter_by(id=(session['current_order_id'])).first()

    return render_template('order.html', items=restaurant.menu, types = meal_types, order_type = curr_order_type)

@customers_bp.route('/takeout')
@employee_redirect
def takeout_page():
    state='takeout'
    return redirect(url_for('customers.contact_form', state=state))

@customers_bp.route('/delivery')
@employee_redirect
def delivery_page():
    state='delivery'
    return redirect(url_for('customers.contact_form', state=state))

@customers_bp.route('/<state>/contact-form', methods=['GET', 'POST'])
@order_active
@employee_redirect
def contact_form(state):

    if state=='takeout':
        form = TakeoutForm()
        
        if form.validate_on_submit():
            """Create new customer from form data and new order, set current order to new order"""
            new_customer = User.register_customer(form.data)
            # pdb.set_trace()
            new_order = Order.create(type='Takeout')
            
            session['current_order_id'] = new_order.id
            session['temp_customer_id'] = new_customer.id

            flash(f"We're pleased to take your order, {new_customer.name}!", 'success')
            return redirect(url_for('customers.order_page'))

    if state=='delivery':
        form = DeliveryForm()
        
        if form.validate_on_submit():
            """Create new customer from form data and new order, set current order to new order"""
            new_customer = User.register_customer(form.data)
            new_order = Order.create(type='Delivery')
            
            session['current_order_id'] = new_order.id
            session['temp_customer_id'] = new_customer.id

            flash(f"We're pleased to take your order, {form.contact_info.data['name']}!", 'success')
            return redirect(url_for('customers.order_page'))

        
    return render_template('contact-form.html', form=form, state=state)

@customers_bp.route('/checkout')
@employee_redirect
def checkout_page():
    # curr_order_type = Order.query.get_or_404(session['current_order_id'])
    curr_order_type = db.session.query(Order.type).filter_by(id=(session['current_order_id'])).first()
    return render_template('checkout.html', order_type=curr_order_type)

@customers_bp.route('/payment', methods=['GET', 'POST'])
@employee_redirect
def payment_page():
    """Set payment method for current order
    
    Returns a rendered payment page
    """
    form = PaymentMethodForm()
    
    if form.validate_on_submit():
        curr_order = Order.query.get(session.get('current_order_id'))
        curr_order.set_payment_method(form.payment_method.data)

        return redirect(url_for('customers.thank_you_page'))

    return render_template('payment-page.html', form=form)

@customers_bp.route('/thank-you')
@employee_redirect
def thank_you_page():   
    """Show thank you page and cleanup session data

    Clears current table assignment and marks the order as complete.
    Removes current order id and customer id from session

    Returns a rendered thank you template
    """

    # make sure user is coming from a valid url
    referrer = request.referrer
    valid_url = url_for('customers.payment_page', _external=True)
    if referrer != valid_url:
        return redirect(url_for('customers.landing_page'))
    
    # validate that curr_table exists before trying to clear it
    curr_table = Table.query.get(session.get('curr_table_num'))
    if curr_table:
        curr_table.free_table()
        session.pop('curr_table_num')

    order = Order.query.get(session.get('current_order_id'))
    order.close()
    
    session.pop('current_order_id')

    if session.get('temp_customer_id'):
        session.pop('temp_customer_id')

    return render_template('thank-you.html', pay_method=order.payment_method)