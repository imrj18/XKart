from models.db import db

# Orders Model
class Order(db.Model):
    __tablename__ = 'order'  # Updated to singular 'order' table name
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)  # Link to Vendor
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to User
    customer_name = db.Column(db.String(150), nullable=False)
    customer_email = db.Column(db.String(150), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Shipped, Delivered, etc.
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # created_at field

    # Relationships
    vendor = db.relationship('Vendor', backref='vendor_orders', lazy=True)  # Renamed backref to 'vendor_orders'
    user = db.relationship('User', backref=db.backref('order', lazy=True))  # Relationship to User


    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
