from models.db import db


class Product(db.Model):
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)  # Ensure this exists
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=False)
    is_top = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    rating = db.Column(db.Float, nullable=True)  # Added rating column

    wishlist_items = db.relationship('Wishlist', back_populates='product', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.title}>'
