from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# Import models to ensure they are registered with SQLAlchemy
from .user import User
from .product import Product
from .order import Order
from .wishlist import Wishlist
