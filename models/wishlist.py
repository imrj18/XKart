from datetime import datetime
from models.db import db
from flask_login import UserMixin


class Wishlist(db.Model, UserMixin):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='wishlist_items')
    product = db.relationship('Product', back_populates='wishlist_items')

    def __repr__(self):
        return f'<Wishlist {self.user_id} - {self.product_id}>'
