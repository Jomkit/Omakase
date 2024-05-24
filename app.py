from flask import Flask, redirect, render_template, flash, url_for
from flask_login import LoginManager, login_user, logout_user
from flask_authorize import Authorize
from flask_debugtoolbar import DebugToolbarExtension
from models.user_models import User
from models.db import connect_db
from forms import LoginForm
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL','postgresql:///omakase'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# Use os.environ here to protect SECRET_KEY
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

debug = DebugToolbarExtension(app)
login = LoginManager(app)
authorize = Authorize(app)

connect_db(app)
app.app_context().push()

############# Register Flask Blueprints ############
from blueprints.customers.customers_routes import customers_bp
app.register_blueprint(customers_bp)

from blueprints.employees.employees_routes import employees_bp
app.register_blueprint(employees_bp, url_prefix='/employees')

from blueprints.api.api_routes import api_bp
app.register_blueprint(api_bp, url_prefix='/omakase/api')
####################################################

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.errorhandler(401)
def unauthorized_access(e):
    """Handle unauthorized access error"""

    # note that we set the 401 status explicitly
    return render_template('/error_pages/custom_error.html', e=e), 401
@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""

    # note that we set the 404 status explicitly
    return render_template('/error_pages/custom_error.html', e=e), 404

login.login_view = 'login'

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
        return redirect(url_for('employees.dashboard'))
        
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()

    flash('Successfully logged out', 'success')
    return redirect(url_for('customers.landing_page'))
