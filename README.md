# 🛒 Flask eCommerce API

A simple RESTful eCommerce API built using **Flask**, **SQLAlchemy**, and **Marshmallow**, connected to a **MySQL** database. It supports users, products, and orders, including many-to-many relationships between orders and products.

---

## 📦 Features

- CRUD operations for Users, Products, and Orders
- Many-to-many relationship between Orders and Products
- Input validation using Marshmallow
- Auto-generation of database tables with SQLAlchemy ORM
- Modular design for easy expansion

---

## 🛠 Tech Stack

- **Python** (Flask)
- **SQLAlchemy** (with Declarative Mapping)
- **MySQL** (Database)
- **Marshmallow** (Serialization & Validation)
- **Flask-SQLAlchemy**, **Flask-Marshmallow**

---

## 🧱 Database Schema

### Users
- `id`: Integer, Primary Key
- `name`: String
- `email`: String (unique)
- `address`: String (optional)

### Products
- `id`: Integer, Primary Key
- `product_name`: String
- `price`: Float

### Orders
- `id`: Integer, Primary Key
- `order_date`: DateTime (defaults to now)
- `user_id`: ForeignKey -> Users

### Order_Product (Association Table)
- `order_id`: ForeignKey -> Orders
- `product_id`: ForeignKey -> Products

---

## 🚀 Getting Started

### 1. Clone the Repository

bash
git clone https://github.com/your-username/flask-ecommerce-api.git
cd flask-ecommerce-api

2. Set Up the Environment
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
3. Configure the Database
Update this line in app.py to match your MySQL credentials:

python
Copy
Edit
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://<username>:<password>@localhost/<database_name>'
Create the database manually in MySQL (e.g., ecommerce_api_db) if it doesn't already exist.

4. Run the App
bash
Copy
Edit
python app.py
Visit: http://127.0.0.1:5000

📫 API Endpoints
Users
Method	Endpoint	Description
POST	/users	Create a user
GET	/users	Get all users
GET	/users/<id>	Get user by ID
PUT	/users/<id>	Update user
DELETE	/users/<id>	Delete user

Products
Method	Endpoint	Description
POST	/products	Create product
GET	/products	Get all products
GET	/products/<id>	Get product by ID
PUT	/products/<id>	Update product
DELETE	/products/<id>	Delete product

Orders
Method	Endpoint	Description
POST	/orders	Create order
PUT	/orders/<order_id>/add_product/<product_id>	Add product to order
DELETE	/orders/<order_id>/remove_product	Remove product (JSON body: {"product_id": x})
GET	/orders/user/<user_id>	Get orders by user ID
GET	/orders/<order_id>/products	Get products in an order

⚠️ Notes
Ensure MySQL is running locally.

Tables are auto-generated at runtime via db.create_all() if they don’t exist.

This project runs in debug=True mode for development. Switch to False in production.

👨‍💻 Author
Jason Breedlove — Built with ❤️ and Flask









