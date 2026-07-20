from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Create database automatically if it doesn't exist
def create_database():
    if not os.path.exists("store.db"):
        import database

create_database()


# ==========================
# Database Connection
# ==========================
def get_connection():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row
    return conn


# ==========================
# Get Products
# ==========================
def get_products(search=""):

    conn = get_connection()
    cursor = conn.cursor()

    if search:
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ?",
            ("%" + search + "%",)
        )
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()
    conn.close()

    return products


# ==========================
# Home Page
# ==========================
@app.route("/")
def home():

    search = request.args.get("search", "")
    category = request.args.get("category", "All")

    products = get_products(search)

    if category != "All":
        products = [
            p for p in products
            if p["category"] == category
        ]

    cart = session.get("cart", {})
    cart_count = sum(cart.values())

    total_price = 0

    all_products = get_products()

    for product in all_products:

        pid = str(product["id"])

        if pid in cart:
            total_price += product["price"] * cart[pid]

    return render_template(
        "index.html",
        products=products,
        cart=cart,
        cart_count=cart_count,
        total_price=total_price,
        user=session.get("user"),
        search=search,
        selected_category=category
    )

    # ==========================
# Add To Cart
# ==========================
@app.route("/add/<int:product_id>")
def add_to_cart(product_id):

    qty = int(request.args.get("qty", 1))

    cart = session.get("cart", {})

    pid = str(product_id)

    if pid in cart:
        cart[pid] += qty
    else:
        cart[pid] = qty

    session["cart"] = cart

    return redirect(request.referrer or url_for("home"))

# ==========================
# Increase Quantity
# ==========================
@app.route("/increase/<int:product_id>")
def increase(product_id):

    cart = session.get("cart", {})

    pid = str(product_id)

    if pid in cart:
        cart[pid] += 1

    session["cart"] = cart

    return redirect(url_for("home"))


# ==========================
# Decrease Quantity
# ==========================
@app.route("/decrease/<int:product_id>")
def decrease(product_id):

    cart = session.get("cart", {})

    pid = str(product_id)

    if pid in cart:

        cart[pid] -= 1

        if cart[pid] <= 0:
            del cart[pid]

    session["cart"] = cart

    return redirect(url_for("home"))


# ==========================
# Remove Item
# ==========================
@app.route("/remove/<int:product_id>")
def remove_item(product_id):

    cart = session.get("cart", {})

    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    session["cart"] = cart

    return redirect(url_for("home"))


# ==========================
# Clear Cart
# ==========================
@app.route("/clear")
def clear_cart():

    session["cart"] = {}

    return redirect(url_for("home"))

# ==========================
# Product Details
# ==========================
@app.route("/product/<int:product_id>")
def product_details(product_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Current Product
    cursor.execute(
        "SELECT * FROM products WHERE id=?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        conn.close()
        return "Product Not Found!"

    # All Products (Related Products માટે)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template(
        "product.html",
        product=product,
        products=products,
        user=session.get("user"),
        cart_count=sum(session.get("cart", {}).values())
    )

# ==========================
# Shopping Cart Page
# ==========================
@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    cart_items = []
    total_price = 0
    cart_count = 0

    conn = get_connection()
    cursor = conn.cursor()

    for pid, qty in cart.items():

        cursor.execute(
            "SELECT * FROM products WHERE id=?",
            (int(pid),)
        )

        product = cursor.fetchone()

        if product:

            item = dict(product)

            item["qty"] = qty

            cart_items.append(item)

            total_price += product["price"] * qty

            cart_count += qty

    conn.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_price=total_price,
        cart_count=cart_count,
        user=session.get("user")
    )

# ==========================
# Wishlist Page
# ==========================
@app.route("/wishlist")
def wishlist():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email FROM users WHERE name=?",
        (session["user"],)
    )

    user = cursor.fetchone()

    if not user:
        conn.close()
        return redirect(url_for("home"))

    cursor.execute("""
        SELECT products.*
        FROM wishlist
        JOIN products
        ON wishlist.product_id = products.id
        WHERE wishlist.user_email=?
    """, (user["email"],))

    products = cursor.fetchall()

    conn.close()

    return render_template(
        "wishlist.html",
        products=products,
        user=session.get("user"),
        cart_count=sum(session.get("cart", {}).values())
    )


# ==========================
# Add To Wishlist
# ==========================
@app.route("/wishlist/add/<int:product_id>")
def add_wishlist(product_id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email FROM users WHERE name=?",
        (session["user"],)
    )

    user = cursor.fetchone()

    if user:

        cursor.execute(
            "SELECT * FROM wishlist WHERE user_email=? AND product_id=?",
            (user["email"], product_id)
        )

        if cursor.fetchone() is None:

            cursor.execute(
                "INSERT INTO wishlist(user_email, product_id) VALUES(?, ?)",
                (user["email"], product_id)
            )

            conn.commit()

    conn.close()

    return redirect(request.referrer or url_for("home"))


# ==========================
# Remove Wishlist
# ==========================
@app.route("/wishlist/remove/<int:product_id>")
def remove_wishlist(product_id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email FROM users WHERE name=?",
        (session["user"],)
    )

    user = cursor.fetchone()

    if user:

        cursor.execute(
            "DELETE FROM wishlist WHERE user_email=? AND product_id=?",
            (user["email"], product_id)
        )

        conn.commit()

    conn.close()

    return redirect(url_for("wishlist"))

    # ==========================
# Checkout
# ==========================
@app.route("/checkout", methods=["POST"])
def checkout():

    session["cart"] = {}

    return """
    <h2 style="text-align:center;margin-top:50px;">
        ✅ Order Placed Successfully!
    </h2>

    <div style="text-align:center;margin-top:20px;">
        <a href="/" style="
            padding:10px 20px;
            background:#0d6efd;
            color:white;
            text-decoration:none;
            border-radius:5px;">
            Continue Shopping
        </a>
    </div>
    """


# ==========================
# Signup
# ==========================
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name, email, password)
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()
            return "❌ Email already exists!"

        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# ==========================
# Login
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user"] = user["name"]

            return redirect(url_for("home"))

        return "❌ Invalid Email or Password"

    return render_template("login.html")


# ==========================
# Logout
# ==========================
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("home"))


# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    app.run(debug=True)