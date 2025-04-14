from datetime import timedelta

from flask import Flask, session, redirect, request, flash, current_app
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_migrate import Migrate
# from dotenv import load_dotenv
# import os
import json

import pdfkit
from sqlalchemy import func

from models import User, Product, Order, category
from models.category import Category

# from models.order import OrderItem

''' wishlist, admin '''
# from models.admin import Admin, Log
from models.cart import Cart
from models.vendor import Vendor
from routes import auth, product, cart, order, vendor, wishlist, admin, category
from models.db import db
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import render_template, send_file, url_for
import qrcode
import os

# Load environment variables
# load_dotenv()

# Application factory function
app = Flask(__name__)

# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    GOOGLE_CLIENT_ID=os.environ.get("GOOGLE_CLIENT_ID"),
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

# Set up configuration from the environment and config.json
try:
    with open('config.json') as config_file:
        config_data = json.load(config_file)
        app.config.update(config_data['params'])
except Exception as e:
    print("Error loading config.json:", e)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app.config['secret_key'])
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', app.config['local_url'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
migrate = Migrate(app, db)

# Initialize database
db.init_app(app)

# Register Blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(product.bp)
app.register_blueprint(cart.bp)
app.register_blueprint(order.bp)
app.register_blueprint(vendor.bp)
app.register_blueprint(wishlist.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(category.bp)


# @login_manager.user_loader
# def load_user(user_id):
#     user = db.session.get(User, int(user_id))
#     if user:
#         print(f"Loaded User: {user.username}")
#         return user
#     vendor = db.session.get(Vendor, int(user_id))
#     if vendor:
#         print(f"Loaded Vendor: {vendor.username}")
#         return vendor
#     return None


# Define application routes
@app.route('/')
def home():
    latest_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    random_products = Product.query.order_by(func.random()).limit(10).all()
    return render_template('index.html', latest_products=latest_products, random_products=random_products)


# ========== Google OAuth Setup ==========
# Load environment variables
load_dotenv()

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


# Google Login route
@app.route('/google-login')
def google_login():
    session['anon_cart'] = session.get('cart', {}).copy()
    return google.authorize_redirect(redirect_uri=url_for('google_callback', _external=True))
    #redirect_uri = url_for('google_callback', _external=True)
    #return google.authorize_redirect(redirect_uri)


@app.route('/google-callback')
def google_callback():
    anon_cart = session.pop('anon_cart', {})  # 🛒 restore temp cart

    token = google.authorize_access_token()
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()

    if not user_info or 'email' not in user_info:
        return "Failed to retrieve user info", 400

    email = user_info['email']
    username = user_info.get('name', 'GoogleUser')

    user = User.query.filter_by(email=email).first()
    if user:
        if not user.is_google_user:
            flash("This email is registered via Email/Password. Please use email login.", "warning")
            return redirect(url_for('auth.login'))
    else:
        user = User(email=email, username=username, is_google_user=True)
        db.session.add(user)
        db.session.commit()

    login_user(user)

    # 🛒 Merge cart from before login
    current_cart = session.get('cart', {})
    for pid, qty in anon_cart.items():
        current_cart[pid] = current_cart.get(pid, 0) + qty
    session['cart'] = current_cart
    session.modified = True

    flash("Logged in with Google successfully", "success")
    return redirect(url_for('home'))


# Optional Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))


@app.route("/index.html")
def index():
    return render_template('index.html')


@app.route('/nearby-vendor', methods=['GET', 'POST'])
def nearby_vendor_page():
    user_city = None
    user_area = None
    vendors = []

    if request.method == 'POST':
        # Get the user's city and area input from the form
        user_city = request.form.get('city')
        user_area = request.form.get('area')

        # Validate inputs
        if user_city and user_area:
            # Query the database for vendors in the same city and area
            vendors = Vendor.query.filter_by(city=user_city, area=user_area).all()
        else:
            flash('Please provide both city and area for better results!', 'danger')

    return render_template('nearby_vendor.html', vendors=vendors, user_city=user_city, user_area=user_area)


@app.route('/search', methods=['GET'])
def search_results():
    # Get the search query from the form
    search_query = request.args.get('search')

    # If search query exists, filter products by name or description
    if search_query:
        products = Product.query.filter(
            (Product.title.ilike(f'%{search_query}%')) |
            (Product.description.ilike(f'%{search_query}%'))
        ).all()
    else:
        # If no search query, return all products
        products = Product.query.all()

    return render_template('search_results.html', products=products, search_query=search_query)


@app.route('/categories')
def categories_page():
    categories = Category.query.all()  # Fetch all categories
    return render_template('categories.html', categories=categories)


@app.route("/product.html")
def product_page():
    return render_template('product.html')


@app.route("/contact.html")
def contact_page():
    return render_template('contact.html')


@login_required
@app.route("/cart.html")
def cart_page():
    return render_template('cart.html')


@app.route("/checkout")
def checkout():
    return render_template('checkout.html')


@app.route('/login.html', methods=['GET', 'POST'])
def login():
    # Your login logic here
    return render_template('login.html')


@app.route('/order_confirmation')
def order_confirmation_page():
    return render_template('order_confirmation.html')


@app.route('/vendor_dashboard.html', endpoint='vendor_dashboard')
def vendor_dashboard():
    return render_template('vendor_dashboard.html')


@app.route('/vendor_register.html', methods=['GET', 'POST'])
def vendor_register():
    # Vendor registration logic here
    return render_template('vendor_register.html')


@app.route('/vendor_login.html', methods=['GET', 'POST'])
def vendor_login():
    # Vendor login logic here
    return render_template('vendor_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/about_us', methods=['GET'])
def about_us():
    return render_template('about_us.html')


@app.route('/privacy_policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')


@app.route('/terms_of_service', methods=['GET'])
def terms_of_service():
    return render_template('terms_of_service.html')


@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')


@app.route('/debug-session')
def debug_session():
    return str(session.get('cart'))


# Vendor login required decorator
def vendor_required(f):
    def wrapper(*args, **kwargs):
        if 'vendor_id' not in session:  # Check if vendor is logged in
            return redirect(url_for('vendor_login'))  # Redirect to vendor login
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__  # Preserve the original function name
    return wrapper


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Try to load the user from the User table first
    user = User.query.get(int(user_id))

    # If not found, try to load the user from the Vendor table
    if not user:
        user = Vendor.query.get(int(user_id))

    return user


@app.context_processor
def inject_cart_count():
    # cart_count = 0
    if current_user.is_authenticated:
        # Fetch cart count from the database for logged-in users
        cart_count = Cart.query.filter_by(user_id=current_user.id).count()
    else:
        # Count cart items stored in the session for anonymous users
        cart_count = sum(session.get('cart', {}).values())
    return dict(cart_count=cart_count)


@app.route('/download-bill/<int:order_id>')
def download_bill(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = order.order_items

    # Generate QR Code
    qr = qrcode.make(
        f"XKart Invoice\nOrder ID: {order.id}\nCustomer: {order.customer_name}\nTotal: ${order.total_amount}"
    )

    qr_dir = os.path.join(current_app.root_path, 'static', 'qr')
    os.makedirs(qr_dir, exist_ok=True)
    qr_path = os.path.join(qr_dir, f'qr_{order.id}.png')
    qr.save(qr_path)

    # Use external URL for QR code in HTML template
    qr_url = url_for('static', filename=f'qr/qr_{order.id}.png', _external=True)

    # Render HTML
    rendered = render_template(
        'invoice.html',
        order=order,
        order_items=order_items,
        qr_code_path=qr_url  # <- Important
    )

    # Configure wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'enable-local-file-access': '',
    }

    pdf_dir = os.path.join(current_app.root_path, 'static', 'bills')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f'invoice_{order.id}.pdf')

    # Generate PDF
    pdfkit.from_string(rendered, pdf_path, configuration=config, options=options)

    return send_file(pdf_path, as_attachment=True)


@app.context_processor
def inject_categories():
    return dict(categories=Category.query.all())


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
