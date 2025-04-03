from flask import request, redirect, url_for, flash, Blueprint, render_template
from flask_login import current_user

from models import User
from models.db import db
from models.wishlist import Wishlist
from models.product import Product


bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')


# Toggle add/remove product to/from wishlist
@bp.route('/toggle/<int:product_id>', methods=['POST'])
def toggle_wishlist(product_id):
    # Get the product from the database
    product = Product.query.get_or_404(product_id)

    # Check if the product is already in the user's wishlist
    wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if wishlist_item:
        # Remove product from wishlist
        db.session.delete(wishlist_item)
        db.session.commit()
    else:
        # Add product to wishlist
        new_wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(new_wishlist_item)
        db.session.commit()

    # Redirect to the previous page (where the button was clicked)
    return redirect(request.referrer)


@bp.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if not current_user.is_authenticated:
        flash("You need to login first.", 'warning')
        return redirect(url_for('login'))

    # Check if user exists
    user = User.query.get(current_user.id)
    if not user:
        flash("User does not exist.", 'warning')
        return redirect(url_for('login'))

    # Check if product exists
    product = Product.query.get_or_404(product_id)

    # Check if the product is already in the wishlist
    existing_wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product.id).first()

    if existing_wishlist_item:
        flash("This product is already in your wishlist.", 'info')
        return redirect(url_for('product.product_detail', product_id=product_id))

    # Add the product to the wishlist
    wishlist_item = Wishlist(user_id=current_user.id, product_id=product.id)
    db.session.add(wishlist_item)
    db.session.commit()

    flash("Product added to wishlist.", 'success')
    return redirect(url_for('product.product_detail', product_id=product_id))


@bp.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    # Check if user is logged in
    if not current_user.is_authenticated:
        flash("You need to login first.", 'warning')
        return redirect(url_for('login'))

    # Get the wishlist item to remove
    wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not wishlist_item:
        flash("This product is not in your wishlist.", 'warning')
        return redirect(url_for('wishlist'))

    # Remove the product from the wishlist
    db.session.delete(wishlist_item)
    db.session.commit()

    flash("Product removed from wishlist.", 'success')
    return redirect(url_for('wishlist'))


@bp.route('/wishlist')
def wishlist():
    # Check if user is logged in
    if not current_user.is_authenticated:
        flash("You need to login first.", 'warning')
        return redirect(url_for('login'))

    # Get all products in the wishlist of the current user
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    products_in_wishlist = [item.product for item in wishlist_items]

    return render_template('wishlist.html', products=products_in_wishlist)
