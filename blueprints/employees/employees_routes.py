############# Employee Routes Blueprint #############

from flask import Blueprint, render_template, redirect, flash, session, url_for, current_app, abort
from models.db import db
from models.user_models import User, Role, Group
from models.restaurant_models import Restaurant
from models.order_models import Order
from models.item_models import MenuItem, Intolerant
from forms import SignupForm, AddMenuItemForm, EditRestaurantForm

from flask_authorize import Authorize
from flask_login import current_user

authorize = Authorize(current_app)

employees_bp = Blueprint("employees", __name__, template_folder='templates')

@employees_bp.route('/edit-restaurant', methods=["GET", "POST"])
@authorize.has_role('manager')
def edit_restaurant():
    """Update restaurant info like restaurant name, address, phone number, description"""
    restaurant = db.session.query(Restaurant).filter_by(id=session['restaurant_id']).first()
    form = EditRestaurantForm(obj=restaurant)
    
    if form.validate_on_submit():
        restaurant.update(form.data)
        
        flash(f'Restaurant information updated', 'success')
        return redirect(url_for('employees.dashboard'))

    return render_template("edit_restaurant.html", form=form, form_name='Edit Restaurant')

@employees_bp.route('/add-employee', methods=["GET", "POST"])
@authorize.has_role('manager')
def employee_signup():
    form = SignupForm()
    form.roles.choices = [(role.name, role.name) for role in db.session.query(Role).all()]

    if form.validate_on_submit(extra_validators=None):

        emp = User.register_employee(form.data)

        flash(f'Employee {emp.username} successfully added', 'success')

        return redirect(url_for('employees.show_employee_list'))

    return render_template('signup.html', form=form, form_name='Add Employee', group='Employees')

@employees_bp.route('/list')
@authorize.in_group('employee')
def show_employee_list():
    employees = User.query.all()

    return render_template('employee-list.html', employees=employees)
    
@employees_bp.route('/employee-dashboard')
@authorize.in_group('employee')
def dashboard():
    """Starting view for employees"""
    restaurant_name = db.session.query(Restaurant.name).filter_by(id=session['restaurant_id']).scalar()
    all_orders = Order.query.all()
    menu_items = MenuItem.query.all()

    return render_template('emp_dashboard.html', restaurant_name=restaurant_name, all_orders=all_orders, menu_items=menu_items)
    
@employees_bp.route('/full-menu')
@authorize.in_group('employee')
def full_menu():
    """Full view of menu"""
    restaurant = Restaurant.query.filter_by(id=session['restaurant_id']).first()
    meal_types = {item.meal_type for item in restaurant.menu}

    return render_template('full_menu.html', items=restaurant.menu, types = meal_types)

# # Future implementation
# @app.route('/kitchen-dashboard')
# @authorize.in_group('employee')
# def kitchen_dashboard():
#     """View of orders for kitchen staff to prepare food"""
#     all_orders = Order.query.all()
#     menu_items = MenuItem.query.all()

#     return render_template('employee/kitchen_dashboard.html', all_orders=all_orders, menu_items=menu_items)

@employees_bp.route('/add-menu-item', methods=["GET","POST"])
@authorize.in_group('employee') 
def add_menu_item():
    menu_item_form = AddMenuItemForm()
    intolerants = Intolerant.query.all()
    menu_item_form.intolerants.choices = [(i.name, i.name) for i in intolerants]
    
    if menu_item_form.validate_on_submit():
        menu_item = MenuItem.add_new_item(menu_item_form.data)

        flash(f'Added {menu_item.name}!', 'success')
        return redirect(url_for('employees.full_menu'))

    return render_template('add_menu_item.html', form=menu_item_form)

@employees_bp.route('/<int:id>/delete', methods=["POST"])
@authorize.has_role('manager')
def delete_user(id):
    """Delete User by id"""

    #NOTE need to cover the case where a manager might accidentally delete themself
    if(current_user.id == id):
        raise abort(401)
    
    res = User.delete(id)
    if(res==None):
        raise abort(404)

    flash(f"Deleted user {id}", "success")
    return redirect(url_for("employees.show_employee_list"))
