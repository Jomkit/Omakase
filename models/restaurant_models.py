from models.db import db
from sqlalchemy.exc import SQLAlchemyError

class Restaurant(db.Model):
    """Restaurant model
    There may be multiple restaurants owned by one entity
    """
    __tablename__ = 'restaurants'

    def __repr__(self):
        return f"<Restaurant #{self.id}, {self.name}>"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, default="Example Restaurant")
    address = db.Column(db.String, nullable=False, default='123 Main Street')
    phone_number = db.Column(db.String(20), default='(123)456-7890')
    description = db.Column(db.Text, default="Example Restaurant, your description of the restaurant would go here")

    menu = db.relationship('MenuItem', secondary="restaurants_menus", backref="restaurants")
    employees = db.relationship('User', backref='restaurant')

    def update(self, restaurant_data):
        """Update new restaurant from input data"""
        for key, value in restaurant_data.items():
            if key != 'csrf_token':
                setattr(self, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return None

class Table(db.Model):
    """Table Model"""
    __tablename__ = 'tables'
    id = db.Column(db.Integer, primary_key=True)
    taken = db.Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def assign(cls, table_number):
        """Set table to taken based on table number"""
        try:
            assigned_table = Table.query.get_or_404(table_number)
            assigned_table.taken = True
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return None
        
    def free_table(self):
        self.taken = False

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return None