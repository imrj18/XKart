# 🛒 XKart – E-Commerce Platform

XKart is a robust e-commerce platform developed using **Flask** and **MySQL**, offering dedicated functionality for both **Customers** and **Vendors**. Customers can browse, search, and purchase products while Vendors can manage their inventory and orders efficiently.

---

## 📚 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation--setup)
- [Usage](#-how-to-use)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## ✨ Features

### 👤 Customer
- Register/login with session or Google OAuth
- Browse/search products
- View product details
- Add to cart & wishlist
- Place orders and checkout
- View/edit profile

### 🧑‍💼 Vendor
- Register/login
- Create/edit/delete products
- View and manage orders
- Edit profile
- Optional: Publish blog/product announcements

### 🔐 Security
- Password hashing with `bcrypt`
- CSRF protection
- Session management

---

## 🧰 Tech Stack

| Layer     | Technology        |
|-----------|-------------------|
| Backend   | Flask (Python)    |
| Database  | MySQL             |
| Frontend  | Jinja2 + Bootstrap|
| Auth      | Flask-Login, OAuth|
| Forms     | Flask-WTF         |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/xkart.git
cd xkart
```

### 2️⃣ Set up a Virtual Environment

### Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a .env file in the root directory:

```bash
SECRET_KEY=your_secret_key
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=xkart
```

### 5️⃣ Set Up the Database

   - Ensure MySQL is running

   - Create a database named xkart

   - (Optional) Use create_db.py or a migration tool to initialize tables

### 6️⃣ Run the Application

```bash
flask run
```

Open http://127.0.0.1:5000/ in your browser.

## 📖 How to Use
### Customers:

   - Register/login

   - Browse products

   - Add to cart or wishlist

   - Checkout and track orders

### Vendors:

   - Register/login

   - Add/edit/delete products

   - View vendor orders

   - Edit profile

## 📂 Project Structure

```bash
XKart/
│
├── app.py
├── create_db.py
├── forms.py
├── requirements.txt
├── .env
├── config.json
├── .gitignore
│
├── models/
│   ├── __init__.py
│   ├── admin.py
│   ├── cart.py
│   ├── category.py
│   ├── db.py
│   ├── order.py
│   ├── product.py
│   ├── user.py
│   ├── vendor.py
│   └── wishlist.py
│
├── routes/
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── cart.py
│   ├── category.py
│   ├── order.py
│   ├── product.py
│   ├── vendor.py
│   └── wishlist.py
│
├── templates/
│   ├── layout.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── cart.html
│   ├── checkout.html
│   ├── product.html
│   ├── product_detail.html
│   ├── add_product.html
│   ├── edit_product.html
│   ├── vendor_register.html
│   ├── vendor_dashboard.html
│   ├── vendor_product.html
│   ├── vendor_view_orders.html
│   ├── user_edit_profile.html
│   ├── change_password.html
│   └── ...more
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── assets/
│   ├── qr/
│   └── bills/
│
└── migrations/
```

## 🤝 Contributing

   1. Fork the project

   2. Clone your fork:

```bash
git clone https://github.com/your-username/xkart.git
cd xkart
```

3. Create a new branch:

```bash
git checkout -b feature-name
```

4. Commit and push:

```bash
    git commit -m "Add feature"
    git push origin feature-name
```

5.  Open a Pull Request 🚀

## 📜 License

This project is licensed under the ![License](https://img.shields.io/github/license/imrj18/xkart).

## 🙏 Acknowledgements

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Bootstrap](https://getbootstrap.com/)

