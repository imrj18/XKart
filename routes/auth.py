import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from models import Order, Wishlist
from models.db import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch user from the database
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            session.permanent = True  # This will apply the permanent session lifetime
            flash('Logged in successfully as User.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


# User Registration
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        city = request.form.get('city')  # New field for city
        area = request.form.get('area')  # New field for area

        # Validate input
        if not username or not email or not password or not confirm_password or not city or not area:
            flash('All fields are required!', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            # Create a new user
            new_user = User(username=username, email=email, password=hashed_password.decode('utf-8'),
                            city=city, area=area)  # Include city and area
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')

    return render_template('register.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch the user's wishlist items
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()

    # Fetch the product details for the wishlist items
    wishlist = [item.product for item in wishlist_items]  # Assuming Wishlist has a product relation

    # Fetch recent orders (if needed)
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()

    return render_template('dashboard.html', wishlist=wishlist, orders=orders)


@bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/user_change_password', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.change_password'))

        # Validate new passwords
        if new_password != confirm_new_password:
            flash('New passwords do not match!', 'danger')
            return redirect(url_for('auth.change_password'))

        # Hash the new password
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        # Update the password in the database
        current_user.password = hashed_new_password.decode('utf-8')
        db.session.commit()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.dashboard'))

    return render_template('user_change_password.html')


@bp.route('/profile')
@login_required
def profile():
    # Logic for the profile page
    return "User profile page"


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('city')
        area = request.form.get('area')

        # Update the user's details
        current_user.name = name
        current_user.city = city
        current_user.area = area

        # Commit the changes to the database
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.dashboard'))

    return render_template('user_edit_profile.html')