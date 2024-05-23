from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.
    
    This should be called in the Flask app
    """

    db.app = app
    db.init_app(app)