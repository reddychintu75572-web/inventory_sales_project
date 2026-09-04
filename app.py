from flask import Flask, render_template, request, redirect
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# MySQL Database Connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="inventory_sales_db"
    )
    return connection


# Home Page
@app.route("/")
def home():
    return render_template("home.html")


# Products Page
@app.route("/products", methods=["GET", "POST"])
def products():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":
        name = request.form["product_name"]
        price = request.form["price"]
        stock = request.form["stock"]

        cursor.execute(
            """
            INSERT INTO products (name, price, stock)
            VALUES (%s, %s, %s)
            """,
            (name, price, stock)
        )

        connection.commit()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "products.html",
        products=products
    )


# Delete Product
@app.route("/delete_product/<int:id>")
def delete_product(id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = %s",
        (id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/products")


# Customers Page
@app.route("/customers", methods=["GET", "POST"])
def customers():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":
        name = request.form["customer_name"]
        phone = request.form["phone"]

        cursor.execute(
            """
            INSERT INTO customers (name, phone)
            VALUES (%s, %s)
            """,
            (name, phone)
        )

        connection.commit()

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "customers.html",
        customers=customers
    )


# Sales Page
@app.route("/sales", methods=["GET", "POST"])
def sales():

    connection = get_db_connection()
    cursor = connection.cursor()

    # Make Sale
    if request.method == "POST":

        customer_id = request.form["customer_id"]
        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])

        # Get Product
        cursor.execute(
            """
            SELECT name, price, stock
            FROM products
            WHERE id = %s
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            cursor.close()
            connection.close()
            return "Product not found"

        product_name = product[0]
        price = float(product[1])
        stock = product[2]

        # Check Stock
        if quantity > stock:
            cursor.close()
            connection.close()
            return "Not enough stock"

        # Get Customer
        cursor.execute(
            """
            SELECT name
            FROM customers
            WHERE id = %s
            """,
            (customer_id,)
        )

        customer = cursor.fetchone()

        if customer is None:
            cursor.close()
            connection.close()
            return "Customer not found"

        customer_name = customer[0]

        # Calculate Total
        total = price * quantity

        # Save Sale
        cursor.execute(
            """
            INSERT INTO sales
            (customer_id, product_id, quantity, total)
            VALUES (%s, %s, %s, %s)
            """,
            (customer_id, product_id, quantity, total)
        )

        # Reduce Stock
        cursor.execute(
            """
            UPDATE products
            SET stock = stock - %s
            WHERE id = %s
            """,
            (quantity, product_id)
        )

        connection.commit()

        # Get Sale Date
        cursor.execute(
            """
            SELECT sale_date
            FROM sales
            ORDER BY id DESC
            LIMIT 1
            """
        )

        sale = cursor.fetchone()
        sale_date = sale[0]

        cursor.close()
        connection.close()

        # Show Bill
        return render_template(
            "bill.html",
            customer_name=customer_name,
            product_name=product_name,
            price=f"{price:.2f}",
            quantity=quantity,
            total=f"{total:.2f}",
            sale_date=sale_date
        )

    # Get Customers
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    # Get Products
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "sales.html",
        customers=customers,
        products=products
    )


# Run Application
if __name__ == "__main__":
    app.run(debug=True)