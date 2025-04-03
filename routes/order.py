from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from models.order import Order, OrderItem
from models.product import Product
from models.db import db
from datetime import datetime
from forms import CheckoutForm

bp = Blueprint('order', __name__, url_prefix='/order')


@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = session.get('cart', {})
    products = Product.query.filter(Product.id.in_(cart_items.keys())).all()
    if request.method == 'POST':
        form = CheckoutForm()
        if form.validate_on_submit():
            order = Order(user_id=current_user.id, total_amount=sum([product.price * cart_items[str(product.id)] for product in products]), date_ordered=datetime.utcnow())
            for product in products:
                order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=cart_items[str(product.id)])
                db.session.add(order_item)
            db.session.add(order)
            db.session.commit()
            session.pop('cart', None)
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order.order_confirmation'))
    else:
        form = CheckoutForm()
    return render_template('checkout.html', products=products, form=form)


@bp.route('/order_confirmation')
@login_required
def order_confirmation():
    return render_template('order_confirmation.html')


@bp.route('/view_orders')
@login_required  # Ensure the user is logged in
def view_orders():
    # Fetch the orders for the current logged-in user
    orders = Order.query.filter_by(user_id=current_user.id).all()  # Assuming each order has a user_id foreign key
    return render_template('view_orders.html', orders=orders)