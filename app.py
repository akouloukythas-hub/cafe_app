from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests
from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

DB = 'cafe.db'
app = Flask(__name__)

# --- Βοηθητική συνάρτηση για DB ---
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # για πρόσβαση με ονόματα πεδίων
    return conn

# --- Αρχική σελίδα ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Παραγγελία τραπεζιού ---
@app.route('/order/table', methods=['GET', 'POST'])
def order_table():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    if request.method == 'POST':
        table_number = request.form['table_number']
        items = request.form.getlist('item')
        qtys = request.form.getlist('qty')

        total = 0
        for pid, q in zip(items, qtys):
            conn = get_db_connection()
            prod = conn.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()
            conn.close()
            total += int(q) * prod['price']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO orders (type, table_number, total) VALUES (?, ?, ?)",
                  ('table', table_number, total))
        order_id = c.lastrowid
        for pid, q in zip(items, qtys):
            prod = conn.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()
            c.execute("INSERT INTO order_items (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                      (order_id, pid, q, prod['price']))
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('order_table.html', products=products)

# --- Παραγγελία delivery ---
@app.route('/order/delivery', methods=['GET', 'POST'])
def order_delivery():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_phone = request.form['customer_phone']
        address = request.form['address']
        items = request.form.getlist('item')
        qtys = request.form.getlist('qty')

        total = 0
        for pid, q in zip(items, qtys):
            conn = get_db_connection()
            prod = conn.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()
            conn.close()
            total += int(q) * prod['price']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO orders (type, customer_name, customer_phone, address, total) VALUES (?, ?, ?, ?, ?)",
                  ('delivery', customer_name, customer_phone, address, total))
        order_id = c.lastrowid
        for pid, q in zip(items, qtys):
            prod = conn.execute("SELECT price FROM products WHERE id=?", (pid,)).fetchone()
            c.execute("INSERT INTO order_items (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                      (order_id, pid, q, prod['price']))
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('order_delivery.html', products=products)

# --- Admin panel ---
@app.route('/admin')
def admin():
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

@app.route('/admin/update_status', methods=['POST'])
def update_status():
    order_id = request.form['order_id']
    new_status = request.form['new_status']
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
    
    return redirect('/admin')

# --- Table map ---
@app.route('/table_map')
def table_map():
    conn = get_db_connection()
    c = conn.cursor()

    # Παίρνουμε όλες τις παραγγελίες τραπεζιών
    c.execute("""
        SELECT id, status, customer_name, total, type, table_number
        FROM orders
        WHERE type='table'
    """)
    rows = c.fetchall()

    tables = []
    for r in rows:
        table_number = int(r['table_number']) if r['table_number'] else None

        # Παίρνουμε τα προϊόντα για κάθε παραγγελία
        c.execute("""
            SELECT p.name, oi.qty, oi.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (r['id'],))
        items = [{"name": row['name'], "qty": row['qty'], "price": row['price']} for row in c.fetchall()]

        tables.append({
            "number": table_number,
            "status": r['status'],
            "customer_name": r['customer_name'],
            "total": r['total'],
            "type": r['type'],
            "items": items
        })

    # Προσθήκη κενών τραπεζιών αν δεν έχουν παραγγελίες
    TOTAL_TABLES = 10
    for n in range(1, TOTAL_TABLES + 1):
        if not any(t['number'] == n for t in tables):
            tables.append({
                "number": n,
                "status": "empty",
                "customer_name": None,
                "total": None,
                "type": "table",
                "items": []
            })

    conn.close()
    return render_template("table_map.html", tables=tables)

# --- Delivery map ---
@app.route('/delivery_map')
def delivery_map():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM orders WHERE type='delivery'")
    orders = c.fetchall()

    deliveries = []
    for o in orders:
        deliveries.append({
            "id": o["id"],
            "customer_name": o["customer_name"],
            "customer_phone": o["customer_phone"],
            "address": o["address"],
            "total": o["total"],
            "status": o["status"],
            "lat": o["lat"],
            "lng": o["lng"],
            "created_at": o["created_at"]
        })

    conn.close()
    return render_template("delivery_map.html", deliveries=deliveries)

# --- Εκτέλεση ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)
