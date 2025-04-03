from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from models import Product, Wishlist
from models.db import db

bp = Blueprint('product', __name__, url_prefix='/product')

from flask import redirect, url_for


@bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id, product_in_wishlist=None):
    product = Product.query.get(product_id)
    if product.stock is None:
        product.stock = 10  # Default stock value
        db.session.commit()
    if not product:
        return "Product not found", 404

    # Handle adding/removing product from wishlist (only for authenticated users)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            message = "You need to log in to modify your wishlist or cart."
            return render_template('product_detail.html', product=product, product_in_wishlist=product_in_wishlist,
                                   popup_message=message)

        # For successful or failure actions:
        flash(f'{product.title} added to wishlist', 'success')  # This can be converted to a modal message as well

        existing_wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()

        if existing_wishlist_item:  # Remove from wishlist
            db.session.delete(existing_wishlist_item)
            flash(f'{product.title} removed from wishlist', 'success')
        else:  # Add to wishlist
            new_wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
            db.session.add(new_wishlist_item)
            flash(f'{product.title} added to wishlist', 'success')

        db.session.commit()  # Commit the changes to the database

    # Check if product is in the wishlist (only if authenticated)
    product_in_wishlist = False
    if current_user.is_authenticated:
        product_in_wishlist = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None

    return render_template('product_detail.html', product=product, product_in_wishlist=product_in_wishlist)

