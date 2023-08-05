"""Database models for the Bull application."""

import datetime

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    """A digital product for sale on our site.

    :param int id: Unique id for this product
    :param str name: Human-readable name of this product
    :param str file_name: Path to file this digital product represents
    :param str version: Optional version to track updates to products
    :param bool is_active: Used to denote if a product should be considered
                          for-sale
    :param float price: Price of product
    """
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    file_name = db.Column(db.String)
    version = db.Column(db.String, default=None, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=True)
    price = db.Column(db.Float)

    def __str__(self):
        """Return the string representation of a product."""
        return '{} (v{})'.format(self.name, self.version)

class Purchase(db.Model):
    """Contains information about the sale of a product.

    :param str uuid: Unique ID (and URL) generated for the customer unique to
                     this purchase
    :param str email: Customer's email address
    :param int product_id: ID of the product associated with this sale
    :param :class:`SQLAlchemy.relationship` product: The associated product
    :param downloads_left int: Number of downloads remaining using this URL
    """
    __tablename__ = 'purchase'
    uuid = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship(Product)
    downloads_left = db.Column(db.Integer, default=5)
    sold_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def sell_date(self):
        return self.sold_at.date

    def __str__(self):
        """Return the string representation of the purchase."""
        return '{} bought by {}'.format(self.product.name, self.email)

class User(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user
    """
    __tablename__ = 'user'

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.is_authenticated = False

    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)

    def is_authenticated(self):
        return self.is_authenticated
    
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email
