# views.py or your Blueprint
from flask import Blueprint, render_template, flash, redirect, url_for

from models import Product
from models.category import Category


bp = Blueprint('category', __name__, url_prefix='/category')


@bp.route('/category/<slug>')
def category_products(slug):
    category = Category.query.filter_by(slug=slug).first()  # Fetch category by slug
    if category:
        products = Product.query.filter_by(category_id=category.id).all()  # Fetch products for that category
        return render_template('category_products.html', category=category, products=products)
    else:
        flash('Category not found', 'danger')
        return redirect(url_for('categories_page'))


