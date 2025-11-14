import sqlite3

DB = 'cafe.db'

products = [
    ('Εσπρέσο', 1.50),
    ('Καπουτσίνο', 2.50),
    ('Φίλτρου', 1.80),
    ('Τσάι', 1.20),
    ('Σάντουιτς', 3.50),
    ('Κρουασάν', 1.80),
    ('Νερό', 0.50),
]

conn = sqlite3.connect(DB)
c = conn.cursor()

# Δημιουργία πινάκων
c.executescript("""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL, -- 'table' ή 'delivery'
    table_number INTEGER, -- για τραπέζια
    customer_name TEXT,
    customer_phone TEXT,
    address TEXT,
    total REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
""")

# Εισαγωγή προϊόντων αν δεν υπάρχουν
c.execute("SELECT COUNT(*) FROM products")
count = c.fetchone()[0]
if count == 0:
    c.executemany("INSERT INTO products (name, price) VALUES (?, ?)", products)
    print("Seeded products.")

conn.commit()
conn.close()
print("DB initialized.")
