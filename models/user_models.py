"""User models"""

from flask_authorize import RestrictionsMixin, AllowancesMixin
from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt
from models.db import db
from models.order_models import Order

# db = SQLAlchemy()
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

# User Model
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
        user = User.query.filter(User.uname==username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        
        return None
    
    @classmethod
    def register_employee(cls, employee_data):
        """Register a new employee for the restaurant"""

        # pass through most data to create new user EXCEPT csrf_token, first_name, last_name, password, and roles. first_name and last_name need to be concatenated and then passed to emp.name, while password needs to be hashed before being passed to emp.password, and user's role must be appended
        # Should make default username = name + id
        employee_info = { k:v for k, v in employee_data.items() if k != 'csrf_token' and k != 'first_name' and k!= 'last_name' and k != 'password' and k != 'roles'}

        new_employee = User(**employee_info)

        name = f"{employee_data['first_name']} {employee_data['last_name']}"
        new_employee.name = name
        new_employee.password = User.hash_pw(employee_data['password'])
        
        try:
            db.session.add(new_employee)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return None

        role = Role.query.filter_by(name=employee_data['roles']).first()
        new_employee.roles.append(role)
        group = Group.query.filter_by(name='employee').first()
        new_employee.groups.append(group)

        # need to set employee username, which relies on the User instanc having an id
        try:
            db.session.commit()
            new_employee.username
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return None

        return new_employee
    
    @classmethod
    def register_customer(cls, customer_data):
        """Register customer, currently only instantiates temporary customers"""
        name = customer_data["contact_info"]['name']
        phone_number = customer_data["contact_info"]['phone_number']

        customer = User(name=name, phone_number=phone_number, temp=True, 
        groups=[Group.query.filter_by(name='customer').first()])

        # try-except adding address info, to handle takeouts that wouldn't have address
        try: 
            proto_add = [field.strip() for field in customer_data['address'].values()]
            address = ", ".join(proto_add)
            customer.address = address
        except KeyError:
            pass

        try:
            db.session.add(customer)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            raise None
        
        return customer
            
    @classmethod
    def delete(cls, user_id):
        """Delete a user"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if(not user):
                return None
                
            User.query.filter_by(id=user_id).delete()
            db.session.commit()
            print(f"User {user_id} deleted")
            return True
        except SQLAlchemy as e:
            db.session.rollback()
            print(e)
            raise None
