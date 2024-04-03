from functools import wraps
from flask import Flask, request, redirect, render_template, flash, url_for, session, jsonify
from flask_login import LoginManager, login_user, logout_user
from flask_authorize import Authorize
from flask_debugtoolbar import DebugToolbarExtension
# from SECRETS import SECRET_KEY
from models import db, connect_db, Restaurant, User, Role, Group, MenuItem, Ingredient, Intolerant, Table, Order, OrderedItems
from forms import AddMenuItemForm, TakeoutForm, DeliveryForm, PaymentMethodForm, SignupForm, LoginForm, SelectTableForm
import os
import json

app = Flask(__name__)
# app.config.from_object(Config)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL','postgresql:///omakase'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

debug = DebugToolbarExtension(app)
login = LoginManager(app)
authorize = Authorize(app)

connect_db(app)
app.app_context().push()

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.errorhandler(401)
def page_not_found(e):
    """Handle unauthorized access error"""

    # note that we set the 401 status explicitly
    return render_template('/error_pages/401.html'), 401

login.login_view = 'login'

############# Custom Decorators ##############
def order_active(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('current_order_id'):

            return redirect(url_for('order_page'))
        return f(*args, **kwargs)
    return decorated_function
##############################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.Authenticate(form.username.data, form.password.data)
        if not user:
            flash('User credentials incorrect, check username and password', 'danger')
            return redirect(url_for('login'))
        login_user(user)

        flash(f'Welcome back {user.username}', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()

    flash('Successfully logged out', 'success')
    return redirect(url_for('landing_page'))

######## Customer Views ##############
@app.route('/')
def landing_page():
    # session.clear()
    restaurant = db.session.query(Restaurant).first()
    session['restaurant_id'] = restaurant.id
    # flash('Welcome Customer!', 'success')
    return render_template('landing.html', restaurant=restaurant)

# @app.route('/signup')

@app.route('/dine-in/select-table', methods=['GET', 'POST'])
@order_active
def assign_table_number():
    """Set up new Order instance and assign table_number, for dining in"""
    # if there's a current order, skip to order page
        
    form = SelectTableForm()
    tables = [(table.id, table.id) for table in Table.query.all() if not table.taken]
    form.table_number.choices = tables
    
    if form.validate_on_submit():
        table_number = form.table_number.data
        
        assigned_table = Table.query.get_or_404(table_number)
        assigned_table.taken = True

        new_order = Order(table_number=table_number)
        db.session.add(new_order)
        db.session.commit()
        session['current_order_id'] = new_order.id
        session['current_table'] = table_number

        flash('Table assigned, enjoy your meal!', 'success')
        return redirect(url_for('order_page'))

    return render_template('select-table-form.html', form=form)

@app.route('/order')
def order_page():
    """Display order page with menu and updating itemized bill on the side"""
    restaurant = db.session.query(Restaurant).first()
    meal_types = {item.meal_type for item in restaurant.menu}
    curr_order_type = db.session.query(Order.type).filter_by(id=(session['current_order_id'])).first()

    return render_template('order.html', items=restaurant.menu, types = meal_types, order_type = curr_order_type)

@app.route('/takeout')
def takeout_page():
    state='takeout'
    return redirect(url_for('contact_form', state=state))

@app.route('/delivery')
def delivery_page():
    state='delivery'
    return redirect(url_for('contact_form', state=state))

@app.route('/<state>/contact-form', methods=['GET', 'POST'])
@order_active
def contact_form(state):

    if state=='takeout':
        form = TakeoutForm()
        
        if form.validate_on_submit():
            name = form.contact_info.data['name']
            phone_number = form.contact_info.data['phone_number']
            customer = User(name=name, phone_number=phone_number, temp=True, 
            groups=[Group.query.filter_by(name='customer').first()])
            new_order = Order(type='Takeout')
            db.session.add_all([customer, new_order])
            db.session.commit()
            
            session['current_order_id'] = new_order.id
            session['temp_customer_id'] = customer.id

            flash(f"We're pleased to take your order, {name}!", 'success')
            return redirect(url_for('order_page'))

    if state=='delivery':
        form = DeliveryForm()
        
        if form.validate_on_submit():
            name = form.contact_info.data['name']
            phone_number = form.contact_info.data['phone_number']
            proto_add = [i.strip() for i in form.address.data.values()]
            address = ", ".join(proto_add)

            customer = User(name=name, phone_number=phone_number, address=address, temp=True, 
            groups=[Group.query.filter_by(name='customer').first()])
            new_order = Order(type='Delivery')
            db.session.add_all([customer, new_order])
            db.session.commit()
            
            session['current_order_id'] = new_order.id
            session['temp_customer_id'] = customer.id

            flash(f"We're pleased to take your order, {name}!", 'success')
            return redirect(url_for('order_page'))

        
    return render_template('contact-form.html', form=form, state=state)

@app.route('/checkout')
def checkout_page():
    # curr_order_type = Order.query.get_or_404(session['current_order_id'])
    curr_order_type = db.session.query(Order.type).filter_by(id=(session['current_order_id'])).first()
    return render_template('checkout.html', order_type=curr_order_type)

@app.route('/payment', methods=['GET', 'POST'])
def payment_page():
    form = PaymentMethodForm()
    
    if form.validate_on_submit():
        curr_order = Order.query.get(session.get('current_order_id'))
        payment_method = form.payment_method.data
        curr_order.payment_method = payment_method
        db.session.commit()

        return redirect(url_for('thank_you_page'))

    return render_template('payment-page.html', form=form)

@app.route('/thank_you')
def thank_you_page():   
    table = Table.query.get(session.get('current_table'))
    if table:
        table.taken = False
    order = Order.query.get(session.get('current_order_id'))
    order.active = False
    order.table_number = None
    db.session.commit()
    
    if table:
        session.pop('current_table')

    session.pop('current_order_id')

    if session.get('temp_customer_id'):
        session.pop('temp_customer_id')

    return render_template('thank-you.html', pay_method=order.payment_method)

######### Employee Views ##############
@app.route('/employees/add-employee', methods=["GET", "POST"])
@authorize.has_role('admin')
def employee_signup():
    form = SignupForm()
    form.roles.choices = [(role.name, role.name) for role in db.session.query(Role).all()]

    if form.validate_on_submit(extra_validators=None):
        # pass through most data to create new user EXCEPT csrf_token, first_name, last_name, password, and roles. first_name and last_name need to be concatenated and then passed to emp.name, while password needs to be hashed before being passed to emp.password, and user's role must be appended
        # Should make default username = name + id, and default password = 1234
        data = { k:v for k, v in form.data.items() if k != 'csrf_token' and k != 'first_name' and k!= 'last_name' and k != 'password' and k != 'roles'}
        emp = User(**data)

        name = f'{form.first_name.data} {form.last_name.data}'
        emp.name = name
        emp.password = User.hash_pw(form.password.data)
        db.session.add(emp)

        role = Role.query.filter_by(name=form.roles.data).first()
        emp.roles.append(role)
        group = Group.query.filter_by(name='employee').first()
        emp.groups.append(group)

        flash(f'Employee {emp.username} successfully added', 'success')
        db.session.commit()
        return redirect(url_for('show_employee_list'))

    return render_template('signup.html', form=form)

@app.route('/employees/list')
@authorize.in_group('employee')
def show_employee_list():
    employees = User.query.all()

    return render_template('/employee/employee-list.html', employees=employees)
    
@app.route('/employee-dashboard')
@authorize.in_group('employee')
def dashboard():
    """Starting view for employees"""
    all_orders = Order.query.all()
    menu_items = MenuItem.query.all()

    return render_template('employee/emp_dashboard.html', all_orders=all_orders, menu_items=menu_items)

# @app.route('/kitchen-dashboard')
# @authorize.in_group('employee')
# def kitchen_dashboard():
#     """View of orders for kitchen staff to prepare food"""
#     all_orders = Order.query.all()
#     menu_items = MenuItem.query.all()

#     return render_template('employee/kitchen_dashboard.html', all_orders=all_orders, menu_items=menu_items)

@app.route('/add-menu-item', methods=["GET","POST"])
@authorize.in_group('employee')
def add_menu_item():
    form = AddMenuItemForm()
    restaurant = Restaurant.query.first()
    intolerants = Intolerant.query.all()
    form.intolerants.choices = [(i.name, i.name) for i in intolerants]
    
    if form.validate_on_submit():
        data = { k:v for k, v in form.data.items() if k != "csrf_token" and k != "intolerants" and k != 'ingredients' }
        # menu_item_data = {**data}
        
        menu_item = MenuItem(**data)

        db.session.add(menu_item)
        db.session.commit()

        MenuItem.add_ingredients(form.ingredients.data, menu_item.id)
        MenuItem.add_intolerants(form.intolerants.data, menu_item.id)
        restaurant.menu.append(menu_item)
        db.session.commit()

        flash(f'Added {menu_item.name}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('/employee/add_menu_item.html', form=form)

############# API routes ##############

@app.route('/omakase/api/orders')
def get_all_orders():
    """Get all order objects and return jsonified"""
    all_orders = Order.query.all()
    data = []

    for order in all_orders:
        data.append(Order.serialize(order))

    return(jsonify(data=data), 200)

@app.route('/omakase/api/order/get_order/<int:id>')
def get_order(id):
    """get an order object and return jsonified order object"""
    order = Order.query.get_or_404(id)

    data = Order.serialize(order)
    return (jsonify(data=data), 200)

@app.route('/omakase/api/order/new', methods=['POST'])
def new_order():
    """Create new order"""
    order = Order(**request.json)   
    db.session.add(order)
    db.session.commit()
    data = Order.serialize(order)
    return (jsonify(data=data), 200)

@app.route('/omakase/api/order/<int:id>/update', methods=['PATCH'])
def update_order(id):
    """Update existing orders"""
    order = Order.query.get_or_404(id)
    update_info = request.json.get('data')
    # Hardcode for now
    for k,v in update_info.items():
        setattr(order, k, v)

    db.session.commit()    
    data = Order.serialize(order)

    return (jsonify(data=data), 200)

@app.route('/omakase/api/order/<int:id>/add_item', methods=['PATCH'])
def add_to_order(id):
    """Add a menu item from id with qty=1 to an existing order"""
    
    order = Order.query.get_or_404(id)
    menu_item_id = request.json.get('menu_item_id')  
    ordered_item = OrderedItems.query.filter(OrderedItems.order_id==id, OrderedItems.menu_item_id==menu_item_id).first()

    # if menu_item has not been on OrderedItems, instantiate (default qty=0)
    if not ordered_item:
        ordered_item = OrderedItems(menu_item_id=menu_item_id)
        order.ordered_items.append(ordered_item)
        db.session.commit()
    
    ordered_item.quantity += 1
    
    db.session.commit()

    data = Order.serialize(order)

    return (jsonify(updated_order=data), 202)

@app.route('/omakase/api/menu/get_menu_item/<int:id>')
def get_menu_item(id):
    menu_item = MenuItem.query.get_or_404(id)

    data = MenuItem.serialize(menu_item)
    
    return (jsonify(data=data), 200)

@app.route('/omakase/api/menu/list_menu_items')
def list_menu_items():
    items = MenuItem.query.all()
    results = [MenuItem.serialize(item) for item in items]

    return (jsonify(data=results), 200)