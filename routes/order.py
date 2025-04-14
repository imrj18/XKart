import io

import qrcode
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from models.order import Order, OrderItem
# from models.product import Product
from models.db import db
# from datetime import datetime
# from forms import CheckoutForm
from models.cart import Cart
from io import BytesIO
from flask import send_file
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

bp = Blueprint('order', __name__, url_prefix='/order')


# @bp.route('/checkout', methods=['GET', 'POST'])
# @login_required
# def checkout():
#     cart_items = session.get('cart', {})
#     products = Product.query.filter(Product.id.in_(cart_items.keys())).all()
#     if request.method == 'POST':
#         form = CheckoutForm()
#         if form.validate_on_submit():
#             order = Order(user_id=current_user.id, total_amount=sum([product.price * cart_items[str(product.id)]
#             for product in products]),
#             date_ordered=datetime.utcnow())
#             for product in products:
#                 order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=cart_items[str(product.id)])
#                 db.session.add(order_item)
#             db.session.add(order)
#             db.session.commit()
#             session.pop('cart', None)
#             flash('Order placed successfully!', 'success')
#             return redirect(url_for('order.order_confirmation'))
#     else:
#         form = CheckoutForm()
#     return render_template('checkout.html', products=products, form=form)


@bp.route('/order-success')
@login_required
def order_confirmation():
    return render_template('order_confirmation.html')

# @bp.route('/order-success')
# @login_required
# def order_success():
#     return render_template('order_success.html')


@bp.route('/view_orders', methods=['GET'])
@login_required
def view_orders():
    # Get all orders for the current logged-in user
    orders = Order.query.filter_by(user_id=current_user.id).all()

    if not orders:
        flash('You have no orders yet.', 'info')

    return render_template('view_orders.html', orders=orders)


@bp.route('/order/<int:order_id>/payment', methods=['GET', 'POST'])
def make_payment(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')

        # Dummy logic: In real life, you'd integrate with Razorpay, Stripe, etc.
        if payment_method:
            order.payment_method = payment_method
            order.payment_status = 'Paid' if payment_method != 'cod' else 'Pending'  # COD is paid on delivery
            db.session.commit()
            flash('Payment processed successfully!', 'success')
            return redirect(url_for('order_confirmation', order_id=order.id))
        else:
            flash('Please select a payment method.', 'danger')

    return render_template('payment.html', order=order)


# @bp.route('/checkout', methods=['POST'])
# @login_required
# def checkout():
#     cart_items = Cart.query.filter_by(user_id=current_user.id).all()
#
#     if not cart_items:
#         flash("Your cart is empty!", "warning")
#         return redirect(url_for('cart.view_cart'))
#
#     if request.method == "POST":
#         # You might collect shipping info here too (optional)
#
#         # Create order
#         order = Order(
#             user_id=current_user.id,
#             vendor_id=cart_items[0].product.vendor_id,
#             customer_name=current_user.name,
#             customer_email=current_user.email,
#             product_name="Multiple Products",  # or leave blank if multiple
#             quantity=sum(item.quantity for item in cart_items),
#             total_amount=sum(item.quantity * item.product.price for item in cart_items),
#             status="Pending"
#         )
#         db.session.add(order)
#         db.session.flush()  # Get order.id before commit
#
#         # Add OrderItems
#         for item in cart_items:
#             order_item = OrderItem(
#                 order_id=order.id,
#                 product_id=item.product_id,
#                 quantity=item.quantity
#             )
#             db.session.add(order_item)
#
#         # Clear cart
#         for item in cart_items:
#             db.session.delete(item)
#
#         db.session.commit()
#
#         flash("Order placed! Please proceed to payment.", "success")
#         return redirect(url_for('order.pay', order_id=order.id))
#
#     return render_template("checkout.html", cart_items=cart_items)

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'GET':
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        total_price = 0
        cart_data = []

        for item in cart_items:
            product = item.product
            if product:
                item_data = {
                    'id': product.id,
                    'name': product.title,
                    'price': product.price,
                    'quantity': item.quantity
                }
                cart_data.append(item_data)
                total_price += product.price * item.quantity

        return render_template('checkout.html', cart_items=cart_data, total_price=total_price)

    # POST Method — Place order
    full_name = request.form['full_name']
    email = request.form['email']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    zip_code = request.form['zip']
    payment_method = request.form['payment_method']

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty", "warning")
        return redirect(url_for('home'))

    # Step 1: Group cart items by vendor
    vendor_groups = {}
    for item in cart_items:
        vendor_id = item.product.vendor_id
        if vendor_id not in vendor_groups:
            vendor_groups[vendor_id] = []
        vendor_groups[vendor_id].append(item)

    # Step 2: Create one order per vendor
    for vendor_id, items in vendor_groups.items():
        total_amount = sum(item.product.price * item.quantity for item in items)
        total_quantity = sum(item.quantity for item in items)

        order = Order(
            vendor_id=vendor_id,
            user_id=current_user.id,
            customer_name=full_name,
            customer_email=email,
            product_name="Multiple",  # optional or remove if not needed
            quantity=total_quantity,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status='Paid' if payment_method != 'cod' else 'Pending',
            status='Confirmed'
        )
        db.session.add(order)
        db.session.flush()  # get order.id

        # Add items to OrderItem
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                quantity=item.quantity
            )
            db.session.add(order_item)

    # Step 3: Clear cart and commit
    Cart.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    flash("Your orders have been placed successfully!", "success")
    return render_template('order_confirmation.html')


@bp.route('/order/<int:order_id>')
@login_required
def view_order_details(order_id):
    order = Order.query.get_or_404(order_id)

    # Only allow the user who placed the order or the vendor to view it
    if current_user.id != order.user_id and current_user.id != order.vendor_id:
        abort(403)

    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    vendor = order.vendor  # Access vendor info from relationship

    return render_template('order_details.html', order=order, order_items=order_items, vendor=vendor)


@bp.route('/delete-order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Optional: Check if the current user is allowed to delete the order
    if order.user_id != current_user.id:
        abort(403)  # Forbidden

    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('your_dashboard_or_order_list_view'))


@bp.route('/update-order-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)

    # Check: only the vendor who owns this order can update it
    if not hasattr(current_user, 'is_vendor') or not current_user.is_vendor or order.vendor_id != current_user.id:
        flash("You don't have permission to update this order.", "danger")
        return redirect(url_for('auth.dashboard'))

    new_status = request.form.get('status')
    if new_status and new_status in ['Pending', 'Processing', 'Completed', 'Cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} updated to '{new_status}'", "success")
    else:
        flash("Invalid status.", "warning")

    return redirect(url_for('order.view_order_details', order_id=order.id))


@bp.route('/vendor/orders')
@login_required
def vendor_view_orders():
    if not hasattr(current_user, 'is_vendor') or not current_user.is_vendor:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('auth.dashboard'))

    orders = Order.query.filter_by(vendor_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('vendor_view_order.html', orders=orders)


@bp.route('/vendor-order/<int:order_id>')
@login_required
def vendor_order_details(order_id):
    order = Order.query.get_or_404(order_id)

    if not hasattr(current_user, 'is_vendor') or current_user.id != order.vendor_id:
        flash("You are not authorized to view this order.", "danger")
        return redirect(url_for('auth.dashboard'))

    order_items = order.order_items
    return render_template('vendor_order_details.html', order=order, order_items=order_items)


# def generate_invoice(order, order_items):
#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=letter)
#
#     width, height = letter
#
#     # Add Title
#     c.setFont("Helvetica-Bold", 20)
#     c.drawString(200, height - 40, "Invoice")
#
#     # Add Order Details
#     c.setFont("Helvetica", 12)
#     c.drawString(30, height - 70, f"Order ID: {order.id}")
#     c.drawString(30, height - 90, f"Customer Name: {order.customer_name}")
#     c.drawString(30, height - 110, f"Email: {order.customer_email}")
#     c.drawString(30, height - 130, f"Order Date: {order.created_at.strftime('%d %B, %Y %I:%M %p')}")
#     c.drawString(30, height - 150, f"Vendor: {order.vendor.shop_name}")
#     c.drawString(30, height - 170, f"Vendor Email: {order.vendor.email}")
#     c.drawString(30, height - 190, f"Payment Method: {order.payment_method}")
#     c.drawString(30, height - 210, f"Payment Status: {order.payment_status}")
#
#     # Draw the table for ordered items
#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(30, height - 240, "Product")
#     c.drawString(300, height - 240, "Quantity")
#     c.drawString(400, height - 240, "Price")
#     c.drawString(500, height - 240, "Total")
#
#     c.setFont("Helvetica", 12)
#     y_position = height - 260
#     total_amount = 0
#     for item in order_items:
#         c.drawString(30, y_position, item.product.title)
#         c.drawString(300, y_position, str(item.quantity))
#         c.drawString(400, y_position, f"${item.product.price:.2f}")
#         item_total = item.product.price * item.quantity
#         c.drawString(500, y_position, f"${item_total:.2f}")
#
#         total_amount += item_total
#         y_position -= 20
#
#     # Add Total Amount
#     c.setFont("Helvetica-Bold", 14)
#     c.drawString(400, y_position - 20, "Total Amount:")
#     c.drawString(500, y_position - 20, f"${total_amount:.2f}")
#
#     # Add footer
#     c.setFont("Helvetica", 10)
#     c.drawString(30, 30, "Thank you for your business!")
#
#     # Save the PDF
#     c.showPage()
#     c.save()
#
#     buffer.seek(0)
#     return buffer
#
#
# @bp.route('/download-bill/<int:order_id>')
# def download_bill(order_id):
#     order = Order.query.get_or_404(order_id)
#     order_items = OrderItem.query.filter_by(order_id=order_id).all()
#
#     pdf_buffer = generate_invoice(order, order_items)
#
#     return send_file(pdf_buffer,
#                      as_attachment=True,
#                      download_name=f"invoice_{order_id}.pdf",
#                      mimetype="application/pdf")

@bp.route('/view-invoice/<int:order_id>')
def view_invoice(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = order.order_items

    # URL for QR image (served by generate_qr)
    qr_code_url = url_for('order.generate_qr', order_id=order.id)

    return render_template(
        'invoice.html',
        order=order,
        order_items=order_items,
        qr_code_url=qr_code_url
    )


@bp.route('/generate-qr/<int:order_id>')
def generate_qr(order_id):
    order = Order.query.get(order_id)
    if not order:
        abort(404)

    qr_data = f"XKart Order ID: {order.id}\nCustomer: {order.customer_name}\nStatus: {order.status}\nAmount: ₹{order.total_amount}"
    qr_img = qrcode.make(qr_data)

    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png')

