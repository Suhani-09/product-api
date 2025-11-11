# app/models.py
"""
This module defines the Product model for the Flask-SQLAlchemy ORM.
"""

from . import db
from sqlalchemy.sql import func

class Product(db.Model):
    """
    Represents a single product entry in the 'product' table.
    """
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, qty={self.quantity})>"
