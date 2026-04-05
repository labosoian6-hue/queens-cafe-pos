"""
database.py - Data layer for CAFE POS System
All SQLite operations live here. No other file writes raw SQL.
"""
import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "cafe_pos.db")


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'cashier',
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        display_order INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL REFERENCES categories(id),
        name TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT DEFAULT '',
        is_available INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_number TEXT UNIQUE NOT NULL,
        capacity INTEGER DEFAULT 4,
        status TEXT DEFAULT 'free'
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER REFERENCES tables(id),
        staff_id INTEGER NOT NULL REFERENCES staff(id),
        status TEXT DEFAULT 'open',
        discount_type TEXT DEFAULT 'percent',
        discount_value REAL DEFAULT 0,
        subtotal REAL DEFAULT 0,
        discount_amount REAL DEFAULT 0,
        tax_amount REAL DEFAULT 0,
        total REAL DEFAULT 0,
        payment_method TEXT DEFAULT '',
        payment_reference TEXT DEFAULT '',
        amount_tendered REAL DEFAULT 0,
        change_given REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        paid_at TEXT DEFAULT '',
        receipt_number TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL REFERENCES orders(id),
        menu_item_id INTEGER REFERENCES menu_items(id),
        item_name TEXT NOT NULL,
        unit_price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        line_total REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)

    # Seed default admin
    existing = c.execute("SELECT id FROM staff WHERE username='admin'").fetchone()
    if not existing:
        c.execute(
            "INSERT INTO staff (username, password_hash, full_name, role) VALUES (?,?,?,?)",
            ("admin", _hash("admin123"), "Administrator", "admin")
        )

    # Seed default categories
    for i, cat in enumerate(["Food", "Drinks", "Snacks", "Specials"]):
        c.execute("INSERT OR IGNORE INTO categories (name, display_order) VALUES (?,?)", (cat, i))

    # Seed default tables
    for t in ["T1", "T2", "T3", "T4", "T5", "T6", "VIP-1", "VIP-2"]:
        c.execute("INSERT OR IGNORE INTO tables (table_number, capacity) VALUES (?,?)",
                  (t, 6 if "VIP" in t else 4))

    # Seed default settings
    defaults = {
        "cafe_name": "MY CAFE",
        "tax_rate": "16",
        "currency_symbol": "KSh",
        "receipt_footer": "Thank you for dining with us!"
    }
    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", (k, v))

    # Seed sample menu items
    food_id = c.execute("SELECT id FROM categories WHERE name='Food'").fetchone()["id"]
    drinks_id = c.execute("SELECT id FROM categories WHERE name='Drinks'").fetchone()["id"]
    snacks_id = c.execute("SELECT id FROM categories WHERE name='Snacks'").fetchone()["id"]
    specials_id = c.execute("SELECT id FROM categories WHERE name='Specials'").fetchone()["id"]

    sample_items = [
        (food_id, "Ugali & Beef", 350, "Ugali served with beef stew"),
        (food_id, "Pilau Rice", 300, "Spiced pilau with kachumbari"),
        (food_id, "Chapati & Beans", 180, "Soft chapati with beans"),
        (food_id, "Fried Eggs & Bread", 150, "Two fried eggs with toast"),
        (food_id, "Pasta Bolognese", 400, "Pasta with minced meat sauce"),
        (drinks_id, "Chai (Tea)", 50, "Hot tea with milk"),
        (drinks_id, "Coffee", 80, "Hot black coffee"),
        (drinks_id, "Mango Juice", 120, "Fresh mango juice"),
        (drinks_id, "Soda (350ml)", 80, "Assorted sodas"),
        (drinks_id, "Water (500ml)", 50, "Mineral water"),
        (snacks_id, "Mandazi", 30, "3 pieces of mandazi"),
        (snacks_id, "Samosa", 40, "2 pieces of samosa"),
        (snacks_id, "Chips (Fries)", 150, "Salted french fries"),
        (snacks_id, "Bhajia", 100, "Potato bhajia with chutney"),
        (specials_id, "Full English Breakfast", 550, "Eggs, sausage, toast, beans"),
        (specials_id, "Chef's Special", 500, "Ask staff for today's special"),
    ]
    for item in sample_items:
        c.execute(
            "INSERT OR IGNORE INTO menu_items (category_id, name, price, description) VALUES (?,?,?,?)",
            item
        )

    conn.commit()
    conn.close()


# ── Receipt Number ─────────────────────────────────────────────────────────────

def generate_receipt_number(conn):
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"RCP-{today}-"
    row = conn.execute(
        "SELECT receipt_number FROM orders WHERE receipt_number LIKE ? ORDER BY receipt_number DESC LIMIT 1",
        (prefix + "%",)
    ).fetchone()
    seq = 1
    if row:
        seq = int(row["receipt_number"].split("-")[-1]) + 1
    return f"{prefix}{seq:04d}"


# ── Staff DAO ──────────────────────────────────────────────────────────────────

def get_all_staff():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM staff ORDER BY full_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_staff_by_username(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM staff WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def verify_password(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM staff WHERE username=? AND password_hash=? AND is_active=1",
        (username, _hash(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_staff(username, password, full_name, role):
    conn = get_connection()
    conn.execute(
        "INSERT INTO staff (username, password_hash, full_name, role) VALUES (?,?,?,?)",
        (username, _hash(password), full_name, role)
    )
    conn.commit()
    conn.close()


def update_staff(staff_id, full_name, role, password=None):
    conn = get_connection()
    if password:
        conn.execute(
            "UPDATE staff SET full_name=?, role=?, password_hash=? WHERE id=?",
            (full_name, role, _hash(password), staff_id)
        )
    else:
        conn.execute(
            "UPDATE staff SET full_name=?, role=? WHERE id=?",
            (full_name, role, staff_id)
        )
    conn.commit()
    conn.close()


def toggle_staff_active(staff_id):
    conn = get_connection()
    conn.execute("UPDATE staff SET is_active = 1 - is_active WHERE id=?", (staff_id,))
    conn.commit()
    conn.close()


# ── Menu DAO ───────────────────────────────────────────────────────────────────

def get_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY display_order, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_items_by_category(category_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM menu_items WHERE category_id=? ORDER BY name", (category_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_items():
    conn = get_connection()
    rows = conn.execute(
        "SELECT mi.*, c.name as category_name FROM menu_items mi "
        "JOIN categories c ON c.id=mi.category_id ORDER BY c.display_order, mi.name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_menu_item(category_id, name, price, description=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO menu_items (category_id, name, price, description) VALUES (?,?,?,?)",
        (category_id, name, price, description)
    )
    conn.commit()
    conn.close()


def update_menu_item(item_id, category_id, name, price, description):
    conn = get_connection()
    conn.execute(
        "UPDATE menu_items SET category_id=?, name=?, price=?, description=? WHERE id=?",
        (category_id, name, price, description, item_id)
    )
    conn.commit()
    conn.close()


def delete_menu_item(item_id):
    conn = get_connection()
    conn.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def toggle_item_availability(item_id):
    conn = get_connection()
    conn.execute("UPDATE menu_items SET is_available = 1 - is_available WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def create_category(name):
    conn = get_connection()
    conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def delete_category(cat_id):
    conn = get_connection()
    conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()


# ── Tables DAO ─────────────────────────────────────────────────────────────────

def get_all_tables():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tables ORDER BY table_number").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_table_status(table_id, status):
    conn = get_connection()
    conn.execute("UPDATE tables SET status=? WHERE id=?", (status, table_id))
    conn.commit()
    conn.close()


def create_table(table_number, capacity):
    conn = get_connection()
    conn.execute("INSERT INTO tables (table_number, capacity) VALUES (?,?)", (table_number, capacity))
    conn.commit()
    conn.close()


def delete_table(table_id):
    conn = get_connection()
    conn.execute("DELETE FROM tables WHERE id=?", (table_id,))
    conn.commit()
    conn.close()


# ── Orders DAO ─────────────────────────────────────────────────────────────────

def create_order(staff_id, table_id=None):
    conn = get_connection()
    receipt_num = generate_receipt_number(conn)
    c = conn.execute(
        "INSERT INTO orders (staff_id, table_id, receipt_number) VALUES (?,?,?)",
        (staff_id, table_id, receipt_num)
    )
    order_id = c.lastrowid
    if table_id:
        conn.execute("UPDATE tables SET status='occupied' WHERE id=?", (table_id,))
    conn.commit()
    conn.close()
    return order_id


def get_open_order_for_table(table_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM orders WHERE table_id=? AND status='open' ORDER BY created_at DESC LIMIT 1",
        (table_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_open_takeaway_order(staff_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM orders WHERE table_id IS NULL AND staff_id=? AND status='open' ORDER BY created_at DESC LIMIT 1",
        (staff_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_order_item(order_id, menu_item_id, item_name, unit_price, quantity=1):
    conn = get_connection()
    # Check if item already in order
    existing = conn.execute(
        "SELECT id, quantity FROM order_items WHERE order_id=? AND menu_item_id=?",
        (order_id, menu_item_id)
    ).fetchone()
    if existing:
        new_qty = existing["quantity"] + quantity
        conn.execute(
            "UPDATE order_items SET quantity=?, line_total=? WHERE id=?",
            (new_qty, new_qty * unit_price, existing["id"])
        )
    else:
        conn.execute(
            "INSERT INTO order_items (order_id, menu_item_id, item_name, unit_price, quantity, line_total) VALUES (?,?,?,?,?,?)",
            (order_id, menu_item_id, item_name, unit_price, quantity, quantity * unit_price)
        )
    _recalculate_order(conn, order_id)
    conn.commit()
    conn.close()


def update_order_item_qty(order_item_id, new_qty):
    conn = get_connection()
    if new_qty <= 0:
        row = conn.execute("SELECT order_id FROM order_items WHERE id=?", (order_item_id,)).fetchone()
        order_id = row["order_id"]
        conn.execute("DELETE FROM order_items WHERE id=?", (order_item_id,))
    else:
        row = conn.execute("SELECT order_id, unit_price FROM order_items WHERE id=?", (order_item_id,)).fetchone()
        order_id = row["order_id"]
        conn.execute(
            "UPDATE order_items SET quantity=?, line_total=? WHERE id=?",
            (new_qty, new_qty * row["unit_price"], order_item_id)
        )
    _recalculate_order(conn, order_id)
    conn.commit()
    conn.close()


def remove_order_item(order_item_id):
    conn = get_connection()
    row = conn.execute("SELECT order_id FROM order_items WHERE id=?", (order_item_id,)).fetchone()
    order_id = row["order_id"]
    conn.execute("DELETE FROM order_items WHERE id=?", (order_item_id,))
    _recalculate_order(conn, order_id)
    conn.commit()
    conn.close()


def set_order_discount(order_id, discount_type, discount_value):
    conn = get_connection()
    conn.execute(
        "UPDATE orders SET discount_type=?, discount_value=? WHERE id=?",
        (discount_type, discount_value, order_id)
    )
    _recalculate_order(conn, order_id)
    conn.commit()
    conn.close()


def _recalculate_order(conn, order_id):
    items = conn.execute(
        "SELECT SUM(line_total) as sub FROM order_items WHERE order_id=?", (order_id,)
    ).fetchone()
    subtotal = items["sub"] or 0.0

    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    tax_rate = float(conn.execute("SELECT value FROM settings WHERE key='tax_rate'").fetchone()["value"]) / 100

    disc_amount = 0.0
    if order["discount_type"] == "percent":
        disc_amount = subtotal * (order["discount_value"] / 100)
    else:
        disc_amount = min(order["discount_value"], subtotal)

    taxable = subtotal - disc_amount
    tax_amount = taxable * tax_rate
    total = taxable + tax_amount

    conn.execute(
        "UPDATE orders SET subtotal=?, discount_amount=?, tax_amount=?, total=? WHERE id=?",
        (subtotal, disc_amount, tax_amount, total, order_id)
    )


def finalize_order(order_id, payment_method, payment_reference="", amount_tendered=0):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    change = max(0, amount_tendered - order["total"])
    conn.execute(
        "UPDATE orders SET status='paid', payment_method=?, payment_reference=?, "
        "amount_tendered=?, change_given=?, paid_at=? WHERE id=?",
        (payment_method, payment_reference, amount_tendered, change, now, order_id)
    )
    if order["table_id"]:
        conn.execute("UPDATE tables SET status='free' WHERE id=?", (order["table_id"],))
    conn.commit()
    conn.close()


def void_order(order_id):
    conn = get_connection()
    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    conn.execute("UPDATE orders SET status='voided' WHERE id=?", (order_id,))
    if order["table_id"]:
        conn.execute("UPDATE tables SET status='free' WHERE id=?", (order["table_id"],))
    conn.commit()
    conn.close()


def get_order_with_items(order_id):
    conn = get_connection()
    order = conn.execute(
        "SELECT o.*, s.full_name as cashier_name, t.table_number "
        "FROM orders o "
        "JOIN staff s ON s.id=o.staff_id "
        "LEFT JOIN tables t ON t.id=o.table_id "
        "WHERE o.id=?", (order_id,)
    ).fetchone()
    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id=?", (order_id,)
    ).fetchall()
    conn.close()
    if not order:
        return None
    return {"order": dict(order), "items": [dict(i) for i in items]}


def get_orders_by_date_range(start_date, end_date, status=None):
    conn = get_connection()
    q = ("SELECT o.*, s.full_name as cashier_name, t.table_number "
         "FROM orders o "
         "JOIN staff s ON s.id=o.staff_id "
         "LEFT JOIN tables t ON t.id=o.table_id "
         "WHERE DATE(o.created_at) BETWEEN ? AND ? ")
    params = [start_date, end_date]
    if status:
        q += "AND o.status=? "
        params.append(status)
    q += "ORDER BY o.created_at DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Reports DAO ────────────────────────────────────────────────────────────────

def get_daily_summary(date_str):
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as orders, SUM(total) as revenue, AVG(total) as avg_order "
        "FROM orders WHERE DATE(paid_at)=? AND status='paid'", (date_str,)
    ).fetchone()
    by_method = conn.execute(
        "SELECT payment_method, COUNT(*) as cnt, SUM(total) as total "
        "FROM orders WHERE DATE(paid_at)=? AND status='paid' GROUP BY payment_method",
        (date_str,)
    ).fetchall()
    conn.close()
    return {
        "summary": dict(row),
        "by_method": [dict(r) for r in by_method]
    }


def get_sales_by_category(date_str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT c.name as category, SUM(oi.line_total) as revenue, SUM(oi.quantity) as qty "
        "FROM order_items oi "
        "JOIN orders o ON o.id=oi.order_id "
        "JOIN menu_items mi ON mi.id=oi.menu_item_id "
        "JOIN categories c ON c.id=mi.category_id "
        "WHERE DATE(o.paid_at)=? AND o.status='paid' "
        "GROUP BY c.name ORDER BY revenue DESC",
        (date_str,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_items(date_str, limit=10):
    conn = get_connection()
    rows = conn.execute(
        "SELECT oi.item_name, SUM(oi.quantity) as qty, SUM(oi.line_total) as revenue "
        "FROM order_items oi "
        "JOIN orders o ON o.id=oi.order_id "
        "WHERE DATE(o.paid_at)=? AND o.status='paid' "
        "GROUP BY oi.item_name ORDER BY qty DESC LIMIT ?",
        (date_str, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Settings DAO ───────────────────────────────────────────────────────────────

def get_setting(key, default=""):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully.")
    print(f"DB path: {DB_PATH}")
