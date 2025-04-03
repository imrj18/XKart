
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from models import Order, Wishlist, Product
from models.admin import Log
from models.db import db
from models.user import User
from flask_login import login_user, logout_user, current_user, login_required

from models.vendor import Vendor

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin' and current_user.role != 'superadmin':
        flash('Access denied!', 'danger')
        return redirect(url_for('auth.login'))

    users_count = User.query.count()
    vendors_count = Vendor.query.count()
    products_count = Product.query.count()
    orders_count = Order.query.count()

    return render_template('admin/dashboard.html',
                           users_count=users_count,
                           vendors_count=vendors_count,
                           products_count=products_count,
                           orders_count=orders_count)


@bp.route('/users')
@login_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


@bp.route('/vendors')
@login_required
def manage_vendors():
    vendors = Vendor.query.all()
    return render_template('admin/manage_vendors.html', vendors=vendors)


@bp.route('/products')
@login_required
def manage_products():
    products = Product.query.all()
    return render_template('admin/manage_products.html', products=products)


@bp.route('/orders')
@login_required
def manage_orders():
    orders = Order.query.all()
    return render_template('admin/manage_orders.html', orders=orders)


@bp.route('/logs')
@login_required
def view_logs():
    logs = Log.query.all()
    return render_template('admin/logs.html', logs=logs)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('admin_settings.html')

