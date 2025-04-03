from flask import Blueprint

bp = Blueprint('main', __name__)

from routes import auth, product, cart, order, vendor
