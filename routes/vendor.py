import os

import bcrypt
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import Order
# from werkzeug.utils import secure_filename
# import os

from models.product import Product
from models.vendor import Vendor
from models.db import db
# from forms import ProductForm

bp = Blueprint('vendor', __name__, url_prefix='/vendor')


# @bp.route('/dashboard')
# @login_required
# def dashboard():
#     if not current_user.is_vendor:
#         flash('You are not authorized to access this page.', 'danger')
#         return redirect(url_for('main.home'))
#
#     products = Product.query.filter_by(user_id=current_user.id).all()
#     return render_template('vendor_dashboard.html', products=products)

#

# Check if the file extension is allowed
# Check if the file extension is allowed

def allowed_file(filename):
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    try:
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            price = float(request.form.get('price'))

            # Handle file upload
            image = request.files.get('image')
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
            else:
                flash('Invalid image file format or no file uploaded', 'danger')
                return redirect(url_for('vendor.add_product'))

            # Create a new product object with the current vendor's ID
            new_product = Product(
                title=title,
                description=description,
                price=price,
                image=filename,
                vendor_id=current_user.id  # Assuming the current_user is a vendor
            )

            # Add the product to the database
            db.session.add(new_product)
            db.session.commit()

            flash('Product added successfully!', 'success')
            return redirect(url_for('vendor.dashboard'))

    except Exception as e:
        print("Error while adding product:", e)
        flash('An error occurred while adding the product.', 'danger')

    return render_template('add_product.html')


@bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    # Fetch the product by ID
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        # Update product details
        product.title = request.form.get('title')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))

        # Handle image update
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            product.image = filename

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('vendor.dashboard'))

    return render_template('edit_product.html', product=product)


@bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_vendor:
        return redirect(url_for('auth.login'))

    # Fetch the product by ID
    product = Product.query.filter_by(id=product_id, vendor_id=current_user.id).first()

    if product:
        # Delete the product from the database
        db.session.delete(product)
        db.session.commit()
        flash('Product has been successfully deleted.', 'success')
    else:
        flash('Product not found or unauthorized action.', 'danger')

    return redirect(url_for('vendor.dashboard'))


# Vendor Registration
@bp.route('/vendor_register', methods=['GET', 'POST'])
def vendor_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        shop_name = request.form.get('shop_name')
        city = request.form.get('city')  # New field for city
        area = request.form.get('area')  # New field for area

        # Validate input
        if not username or not email or not password or not confirm_password or not city or not area:
            flash('All fields are required!', 'danger')
            return render_template('vendor_register.html')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('vendor_register.html')

        if Vendor.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('vendor_register.html')

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            # Create a new vendor
            new_vendor = Vendor(username=username, email=email, password=hashed_password.decode('utf-8'),
                                shop_name=shop_name, city=city, area=area)  # Include city and area
            db.session.add(new_vendor)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('vendor.vendor_login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')

    return render_template('vendor_register.html')


# Vendor Login
@bp.route('/vendor_login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch user from the database
        vendor = Vendor.query.filter_by(email=email).first()

        if vendor and bcrypt.checkpw(password.encode('utf-8'), vendor.password.encode('utf-8')):
            login_user(vendor)
            session.permanent = True  # This will apply the permanent session lifetime
            flash('Logged in successfully as Vendor.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('vendor_login.html')


# Vendor Logout
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))


@bp.route('/vendor_dashboard')
@login_required
def dashboard():
    if not current_user.is_vendor:
        return redirect(url_for('auth.login'))

    # Fetch products associated with the vendor
    vendor_products = Product.query.filter_by(vendor_id=current_user.id).all()

    # Debugging
    print("Vendor ID:", current_user.id)
    print("Products for Vendor:", vendor_products)

    return render_template('vendor_dashboard.html', products=vendor_products)


@bp.route('/profile')
@login_required
def profile():
    # Logic for the profile page
    return render_template('vendor_profile.html', user=current_user)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        print("Form data:", request.form)

        print("Passwords received:", old_password, new_password, confirm_new_password)  # Debugging

        # Check if old password is correct
        if not bcrypt.checkpw(old_password.encode('utf-8'), current_user.password.encode('utf-8')):
            flash('Old password is incorrect!', 'danger')
            return redirect(url_for('vendor.change_password'))

        # Validate new passwords
        if new_password != confirm_new_password:
            flash('New passwords do not match!', 'danger')
            return redirect(url_for('vendor.change_password'))

        # Hash the new password
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        # Update the password in the database
        current_user.password = hashed_new_password.decode('utf-8')
        db.session.commit()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('vendor.dashboard'))

    return render_template('change_password.html')


# Edit Profile Route
@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Get the form data
        username = request.form.get('username')
        email = request.form.get('email')
        shop_name = request.form.get('shop_name')

        # Update the vendor profile
        current_user.username = username
        current_user.email = email
        current_user.shop_name = shop_name
        db.session.commit()

        flash('Profile successfully updated', 'success')
        return redirect(url_for('vendor.profile'))

    # Render the edit profile page, passing current_user to the template
    return render_template('edit_vendor_profile.html', user=current_user)


@bp.route('/view_order_details/<int:order_id>')
@login_required
def view_order_details(order_id):
    order = Order.query.get_or_404(order_id)
    if order.vendor_id != current_user.id:
        return redirect(url_for('vendor.view_orders'))
    return render_template('view_order_details.html', order=order)


@bp.route('/view-orders')
@login_required
def view_orders():
    # Fetch orders for the logged-in vendor
    orders = Order.query.filter_by(vendor_id=current_user.id).all()
    return render_template('view_orders.html', orders=orders)


@bp.route('/vendor/<int:vendor_id>/products')
def vendor_products(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    products = Product.query.filter_by(vendor_id=vendor_id).all()  # Get all products of this vendor
    return render_template('vendor_product.html', vendor=vendor, products=products)

