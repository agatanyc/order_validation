from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy()

class Order(db.Model):

    __tablename__ = 'orders'

    primary_key = db.Column(db.Integer, autoincrement=True, primary_key=True)
    order_id = db.Column(db.Integer())
    o_name = db.Column(db.String(40))
    o_state = db.Column(db.String(40))
    o_email = db.Column(db.String(40))
    o_zip_code = db.Column(db.Integer())
    o_DOB = db.Column(db.String(40))
    valid = db.Column(db.String(40))
    errors = db.relationship('Error', back_populates='order')

class Error(db.Model):

    __tablename__ = 'errors'

    primary_key = db.Column(db.Integer, autoincrement=True, primary_key=True)
    e_name = db.Column(db.String(60))
    order_key = db.Column(db.Integer, db.ForeignKey('orders.primary_key'), nullable=False)
    order = db.relationship('Order', back_populates='errors')

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
    db.app = app
    db.init_app(app)


if __name__ == '__main__':

    init_db(app)
    db.create_all()

    print "Connected to DB"
