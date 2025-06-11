from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, String, Float, DateTime, select, func
from marshmallow import ValidationError
from typing import List, Optional
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
# connects the app to MySQL database using SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Tank0408!@localhost/ecommerce_api_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy Base class
class Base(DeclarativeBase):
    pass

# Initialize DB and Marshmallow (handles the ORM)

db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# ----------------------------
# Association Table
# ----------------------------
# many to many bridge connecting orders to products

order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)

# ----------------------------
# MODELS
# ----------------------------
# Stores basic user data

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")
    
# Represents items for sale
class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

# Represents purchases, connected to a User and multiple Products.
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    products: Mapped[List["Product"]] = relationship("Product", secondary=order_product)

# ----------------------------
# SCHEMAS
# ----------------------------
# Auto-generates serialization and deserialization logic using Marshmellow for each model.
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# ----------------------------
# ROUTES: Users
# ----------------------------
# Post creates a user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_user = User(name=user_data['name'], address=user_data['address'], email=user_data['email'])
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201
# Get returns all users
@app.route('/users', methods=['GET'])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return users_schema.jsonify(users), 200
# Get (id) returns a user by id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200
# Put allows you to edit user info
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    user.name = user_data['name']
    user.email = user_data['email']
    user.address = user_data.get('address')
    db.session.commit()
    return user_schema.jsonify(user), 200

# Delete is used to delete a user by id
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Deleted user {id}"}), 200

# ----------------------------
# ROUTES: Products
# ----------------------------
# Create Products
@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_product = Product(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product), 201

# Get all Products
@app.route('/products', methods=['GET'])
def get_products():
    products = db.session.execute(select(Product)).scalars().all()
    return products_schema.jsonify(products), 200

# Get Product by id
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    return product_schema.jsonify(db.session.get(Product, id)), 200

# Edit a Product by id
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    try:
        data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = data['product_name']
    product.price = data['price']
    db.session.commit()
    return product_schema.jsonify(product), 200

# Delete a Product by id
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Deleted product {id}"}), 200

# ----------------------------
# ROUTES: Orders
# ----------------------------
# Create a new Order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_order = Order(order_date=order_data['order_date'], user_id=order_data['user_id'])
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order), 201

# Add Product to an Order
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if product in order.products:
        return jsonify({"message": "Product already in order"}), 400

    order.products.append(product)
    db.session.commit()
    return jsonify({"message": "Product added to order"}), 200

# Deletes Product from an Order
@app.route('/orders/<int:order_id>/remove_product', methods=['DELETE'])
def remove_product_from_order(order_id):
    product_id = request.json.get('product_id')
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if product not in order.products:
        return jsonify({"message": "Product not in order"}), 400

    order.products.remove(product)
    db.session.commit()
    return jsonify({"message": "Product removed from order"}), 200

# Get all Orders by user id
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_by_user(user_id):
    orders = db.session.execute(select(Order).where(Order.user_id == user_id)).scalars().all()
    return orders_schema.jsonify(orders), 200

# Get all Products in an order using Order id
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_in_order(order_id):
    order = db.session.get(Order, order_id)
    return products_schema.jsonify(order.products), 200

# ----------------------------
# Start the app
# ----------------------------
# Ensures all tables are created before starting the Flask server.
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
