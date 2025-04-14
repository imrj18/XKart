import json

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from models.cart import Cart
from models.product import Product, db

bp = Blueprint('cart', __name__, url_prefix='/cart')


@bp.route('/list')
def product_list():
    """Display a list of all products."""
    try:
        products = Product.query.all()
        return render_template('product_list.html', products=products)
    except SQLAlchemyError:
        flash('Error fetching products. Please try again later.', 'danger')
        return redirect(url_for('home'))


@bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Hybrid add-to-cart function for both session and logged-in users."""
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('home'))

    quantity = int(request.form.get('quantity', 1))

    if current_user.is_authenticated:
        # Logged-in user: Store in database
        cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            new_cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
            db.session.add(new_cart_item)
        db.session.commit()
    else:
        # Guest user: Store in session
        cart = session.get('cart', {})

        # Convert keys to string (ensuring consistency)
        product_id_str = str(product_id)
        cart[product_id_str] = cart.get(product_id_str, 0) + quantity

        # Save back to session
        session['cart'] = cart
        session.modified = True

    # Debugging: Print session data after adding a product
    print("Updated Session Cart:", session['cart'])

    flash("Product added to cart!", "success")
    return redirect(url_for('cart.view_cart'))


@bp.route('/view', methods=['GET'])
def view_cart():
    """View cart items for both guest and logged-in users."""
    cart_items = {}

    if current_user.is_authenticated:
        # Fetch items from database for logged-in users
        cart_products = Cart.query.filter_by(user_id=current_user.id).all()
        for item in cart_products:
            cart_items[item.product_id] = item.quantity
    else:
        # Fetch items from session (convert keys to int)
        session_cart = session.get('cart', {})
        cart_items = {int(k): v for k, v in session_cart.items()}

    # Fetch product details
    products = Product.query.filter(Product.id.in_(cart_items.keys())).all()

    # Debugging: Print product details
    total_price = 0
    for product in products:
        product_quantity = cart_items.get(product.id, 0)
        product_total = product.price * product_quantity
        total_price += product_total
        print(f"Product: {product.title}, Price: {product.price}, Quantity: {product_quantity}, Subtotal: {product_total}")

    print("Final Total Price:", total_price)

    return render_template('cart.html', products=products, cart_items=cart_items, total_price=total_price)


@bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Remove a product from the cart."""
    try:
        if current_user.is_authenticated:
            cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
                flash('Product removed from cart.', 'success')
            else:
                flash('Product not found in your cart.', 'warning')
        else:
            cart = session.get('cart', {})
            if str(product_id) in cart:
                del cart[str(product_id)]
                session['cart'] = cart
                session.modified = True
                flash('Product removed from cart.', 'success')
            else:
                flash('Product not found in your cart.', 'warning')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Error removing product from cart. Please try again.', 'danger')

    return redirect(url_for('cart.view_cart'))


@bp.route('/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    """Update the quantity of an item in the cart."""
    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    if current_user.is_authenticated:
        cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity = quantity
            db.session.commit()
    else:
        cart = session.get('cart', {})
        cart[str(product_id)] = quantity
        session['cart'] = cart
        session.modified = True

    flash("Cart updated!", "success")
    return redirect(url_for('cart.view_cart'))


# @bp.route('/checkout', methods=['GET', 'POST'])
# @login_required
# def checkout():
#     cart = session.get('cart', {})
#     cart_items = []
#     total_price = 0
#
#     # Fetch product details from DB
#     for product_id, quantity in cart.items():
#         product = Product.query.get(int(product_id))
#         if product:
#             subtotal = product.price * quantity
#             total_price += subtotal
#             cart_items.append({
#                 'id': product.id,
#                 'name': product.title,
#                 'price': product.price,
#                 'quantity': quantity
#             })
#
#     # Handle form submission
#     if request.method == 'POST':
#         full_name = request.form['full_name']
#         email = request.form['email']
#         address = request.form['address']
#         city = request.form['city']
#         state = request.form['state']
#         zip_code = request.form['zip']
#
#         # Optional: Save order to DB
#         # order = Order(user_id=current_user.id, total=total_price, status='Placed', ...)
#         # db.session.add(order)
#         # db.session.commit()
#
#         flash('Your order has been placed successfully!', 'success')
#         session.pop('cart', None)  # Clear cart after order
#         return redirect(url_for('home'))  # or redirect to 'order_success'
#
#     return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

