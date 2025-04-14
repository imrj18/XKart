from flask_login import UserMixin
from models.db import db  # Import db from models/db.py


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    city = db.Column(db.String(100), nullable=True, default='Unknown')
    area = db.Column(db.String(100), nullable=True, default='Unknown')
    is_vendor = db.Column(db.Boolean, default=False)
    is_google_user = db.Column(db.Boolean, default=False)

    # Link to the Order model
    orders = db.relationship('Order', back_populates='user', cascade='all, delete-orphan')
    wishlist_items = db.relationship('Wishlist', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def is_vendor(self):
        return False

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def create_user(cls, username, email, password):
        new_user = cls(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return new_user
