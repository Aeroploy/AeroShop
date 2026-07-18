import sqlite3

# ==========================
# Connect Database
# ==========================
conn = sqlite3.connect("store.db")
cursor = conn.cursor()

# ==========================
# Products Table
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    image TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    rating REAL DEFAULT 4.5
)
""")

# ==========================
# Users Table
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# Wishlist Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS wishlist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    product_id INTEGER NOT NULL
)
""")

# ==========================
# Products Data
# ==========================
products = [

("T-Shirt",499,"tshirt.jpg","Clothing",
"Premium cotton T-Shirt with soft fabric and comfortable fit.",4.4),

("Shoes",1999,"shoes.jpg","Footwear",
"Lightweight running shoes suitable for daily use.",4.8),

("Watch",2999,"watch.jpg","Accessories",
"Stylish wrist watch with premium quality.",4.6),

("Laptop",55999,"laptop.jpg","Electronics",
"High performance laptop for coding, office work and gaming.",4.9),

("Mobile",18999,"mobile.jpg","Electronics",
"Latest Android smartphone with fast processor.",4.7),

("Headphone",2999,"headphone.jpg","Electronics",
"Wireless Bluetooth headphone with HD sound quality.",4.5)

]

# ==========================
# Insert Products
# ==========================
cursor.execute("SELECT COUNT(*) FROM products")

count = cursor.fetchone()[0]

if count == 0:

    cursor.executemany("""

    INSERT INTO products
(name, price, image, category, description, rating)
VALUES (?, ?, ?, ?, ?, ?)

    """, products)

conn.commit()
conn.close()

print("✅ Database Ready Successfully")