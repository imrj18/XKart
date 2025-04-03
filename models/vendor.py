from models.db import db
from flask_login import UserMixin


# Vendor Model
class Vendor(db.Model, UserMixin):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    shop_name = db.Column(db.String(150))
    city = db.Column(db.String(100), nullable=True, default='Unknown')
    area = db.Column(db.String(100), nullable=True, default='Unknown')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Link to the Order model
    orders = db.relationship('Order', back_populates='vendor', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='vendor', lazy=True)

    def __repr__(self):
        return f'<Vendor {self.username}>'

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def create_vendor(cls, username, email, password, shop_name):
        new_vendor = cls(username=username, email=email, password=password, shop_name=shop_name)
        db.session.add(new_vendor)
        db.session.commit()
        return new_vendor

    @property
    def is_vendor(self):
        return True
