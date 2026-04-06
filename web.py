"""
web.py - Flask web dashboard for QUEENS CAFE POS
Run: python web.py  → open http://localhost:5000
"""
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import database
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
database.initialize_db()

app = Flask(__name__)
app.secret_key = "queenscafe2024secret"
app.jinja_env.globals["enumerate"] = enumerate

# ── Auth ───────────────────────────────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        if session["user"].get("role") != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ── Login ──────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        user = database.verify_password(
            request.form["username"], request.form["password"]
        )
        if user:
            session["user"] = dict(user)
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error,
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    summary = database.get_daily_summary(today)
    top_items = database.get_top_items(today, limit=5)
    by_cat = database.get_sales_by_category(today)
    recent_orders = database.get_orders_by_date_range(today, today)[:8]
    # Table status summary for dashboard
    all_tables = database.get_all_tables()
    tables_free = sum(1 for t in all_tables if t["status"] == "free")
    tables_occupied = sum(1 for t in all_tables if t["status"] == "occupied")
    tables_reserved = sum(1 for t in all_tables if t["status"] == "reserved")
    # Open orders count
    open_orders_count = database.get_open_orders_count()
    return render_template("dashboard.html",
                           summary=summary,
                           top_items=top_items,
                           by_cat=by_cat,
                           recent_orders=recent_orders,
                           open_orders_count=open_orders_count,
                           tables_free=tables_free,
                           tables_occupied=tables_occupied,
                           tables_reserved=tables_reserved,
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           user=session["user"])


# ── Menu Management ────────────────────────────────────────────────────────────
@app.route("/menu")
@login_required
def menu():
    categories = database.get_categories()
    all_items = database.get_all_items()
    return render_template("menu.html",
                           categories=categories,
                           items=all_items,
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           user=session["user"])

@app.route("/menu/add", methods=["POST"])
@login_required
def add_menu_item():
    try:
        database.create_menu_item(
            int(request.form["category_id"]),
            request.form["name"].strip(),
            float(request.form["price"]),
            request.form.get("description", "").strip()
        )
        flash(f"'{request.form['name']}' added successfully.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("menu"))

@app.route("/menu/edit/<int:item_id>", methods=["POST"])
@login_required
def edit_menu_item(item_id):
    try:
        database.update_menu_item(
            item_id,
            int(request.form["category_id"]),
            request.form["name"].strip(),
            float(request.form["price"]),
            request.form.get("description", "").strip()
        )
        flash("Item updated.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("menu"))

@app.route("/menu/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_menu_item(item_id):
    database.delete_menu_item(item_id)
    flash("Item deleted.", "success")
    return redirect(url_for("menu"))

@app.route("/menu/toggle/<int:item_id>", methods=["POST"])
@login_required
def toggle_item(item_id):
    database.toggle_item_availability(item_id)
    return redirect(url_for("menu"))

@app.route("/menu/import", methods=["POST"])
@login_required
def import_menu_csv():
    import csv, io
    f = request.files.get("csv_file")
    if not f:
        flash("No file selected.", "error")
        return redirect(url_for("menu"))
    stream = io.StringIO(f.stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)
    count = 0
    cats = {c["name"].lower(): c["id"] for c in database.get_categories()}
    for row in reader:
        cat_name = row.get("category", "").strip().lower()
        cat_id = cats.get(cat_name)
        if not cat_id:
            database.create_category(row.get("category", "Other").strip())
            cats = {c["name"].lower(): c["id"] for c in database.get_categories()}
            cat_id = cats[cat_name]
        try:
            database.create_menu_item(cat_id, row["name"].strip(),
                                      float(row["price"]),
                                      row.get("description", "").strip())
            count += 1
        except Exception:
            pass
    flash(f"Imported {count} items.", "success")
    return redirect(url_for("menu"))


# ── Categories ─────────────────────────────────────────────────────────────────
@app.route("/menu/add-category", methods=["POST"])
@login_required
def add_category():
    name = request.form.get("name", "").strip()
    if name:
        try:
            database.create_category(name)
            flash(f"Category '{name}' added.", "success")
        except Exception as e:
            flash(str(e), "error")
    return redirect(url_for("menu"))

@app.route("/menu/delete-category/<int:cat_id>", methods=["POST"])
@admin_required
def delete_category(cat_id):
    items = database.get_items_by_category(cat_id)
    for i in items:
        database.delete_menu_item(i["id"])
    database.delete_category(cat_id)
    flash("Category and its items deleted.", "success")
    return redirect(url_for("menu"))


# ── Settings ───────────────────────────────────────────────────────────────────
@app.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        for key in ["cafe_name", "tax_rate", "currency_symbol", "receipt_footer",
                    "address", "phone", "kra_pin", "receipt_header"]:
            database.set_setting(key, request.form.get(key, "").strip())
        flash("Settings saved successfully.", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html",
                           cafe_name=database.get_setting("cafe_name"),
                           tax_rate=database.get_setting("tax_rate"),
                           currency_symbol=database.get_setting("currency_symbol"),
                           receipt_footer=database.get_setting("receipt_footer"),
                           address=database.get_setting("address"),
                           phone=database.get_setting("phone"),
                           kra_pin=database.get_setting("kra_pin"),
                           receipt_header=database.get_setting("receipt_header"),
                           user=session["user"])


# ── Setup Wizard ───────────────────────────────────────────────────────────────
@app.route("/setup", methods=["GET", "POST"])
@admin_required
def setup():
    if request.method == "POST":
        step = request.form.get("step")

        if step == "settings":
            database.set_setting("cafe_name", request.form["cafe_name"].strip())
            database.set_setting("tax_rate", request.form["tax_rate"].strip())
            database.set_setting("currency_symbol", request.form["currency_symbol"].strip())
            database.set_setting("receipt_footer", request.form["receipt_footer"].strip())
            flash("Basic settings saved.", "success")

        elif step == "category":
            name = request.form.get("name", "").strip()
            if name:
                try:
                    database.create_category(name)
                    flash(f"Category '{name}' added.", "success")
                except Exception as e:
                    flash(str(e), "error")

        elif step == "item":
            try:
                database.create_menu_item(
                    int(request.form["category_id"]),
                    request.form["name"].strip(),
                    float(request.form["price"]),
                    request.form.get("description", "").strip()
                )
                flash(f"'{request.form['name']}' added.", "success")
            except Exception as e:
                flash(str(e), "error")

        elif step == "staff":
            try:
                database.create_staff(
                    request.form["username"].strip(),
                    request.form["password"],
                    request.form["full_name"].strip(),
                    request.form["role"]
                )
                flash(f"Staff '{request.form['full_name']}' added.", "success")
            except Exception as e:
                flash(str(e), "error")

        elif step == "tables":
            try:
                database.create_table(
                    request.form["table_number"].strip(),
                    int(request.form["capacity"])
                )
                flash(f"Table '{request.form['table_number']}' added.", "success")
            except Exception as e:
                flash(str(e), "error")

        return redirect(url_for("setup"))

    categories = database.get_categories()
    all_items = database.get_all_items()
    all_staff = database.get_all_staff()
    all_tables = database.get_all_tables()
    return render_template("setup.html",
                           categories=categories,
                           items=all_items,
                           staff=all_staff,
                           tables=all_tables,
                           cafe_name=database.get_setting("cafe_name"),
                           tax_rate=database.get_setting("tax_rate"),
                           currency_symbol=database.get_setting("currency_symbol"),
                           receipt_footer=database.get_setting("receipt_footer"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           user=session["user"])


# ── Staff ──────────────────────────────────────────────────────────────────────
@app.route("/staff")
@admin_required
def staff():
    return render_template("staff.html",
                           staff=database.get_all_staff(),
                           cafe_name=database.get_setting("cafe_name"),
                           user=session["user"])

@app.route("/staff/add", methods=["POST"])
@admin_required
def add_staff():
    try:
        database.create_staff(
            request.form["username"].strip(),
            request.form["password"],
            request.form["full_name"].strip(),
            request.form["role"]
        )
        flash("Staff member added.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("staff"))

@app.route("/staff/toggle/<int:staff_id>", methods=["POST"])
@admin_required
def toggle_staff(staff_id):
    database.toggle_staff_active(staff_id)
    return redirect(url_for("staff"))

@app.route("/staff/edit/<int:staff_id>", methods=["POST"])
@admin_required
def edit_staff(staff_id):
    password = request.form.get("password", "").strip()
    database.update_staff(
        staff_id,
        request.form["full_name"].strip(),
        request.form["role"],
        password if password else None
    )
    flash("Staff member updated.", "success")
    return redirect(url_for("staff"))

@app.route("/staff/delete/<int:staff_id>", methods=["POST"])
@admin_required
def delete_staff_route(staff_id):
    s = database.get_staff_by_id(staff_id)
    if s and s["username"] == "admin":
        flash("Cannot delete the default admin account.", "error")
    else:
        database.delete_staff(staff_id)
        flash("Staff member deleted.", "success")
    return redirect(url_for("staff"))


# ── Reports ────────────────────────────────────────────────────────────────────
@app.route("/reports")
@login_required
def reports():
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    start = request.args.get("start", today)
    end = request.args.get("end", today)
    summary = database.get_range_summary(start, end)
    top_items = database.get_top_items_range(start, end, limit=10)
    by_cat = database.get_sales_by_category_range(start, end)
    orders = database.get_orders_by_date_range(start, end, status="paid")
    breakdown = database.get_daily_breakdown(start, end) if start != end else []
    return render_template("reports.html",
                           summary=summary,
                           top_items=top_items,
                           by_cat=by_cat,
                           orders=orders,
                           breakdown=breakdown,
                           start=start, end=end,
                           currency=database.get_setting("currency_symbol", "KSh"),
                           cafe_name=database.get_setting("cafe_name"),
                           user=session["user"])


# ── Tables ─────────────────────────────────────────────────────────────────────
@app.route("/tables")
@login_required
def tables():
    return render_template("tables.html",
                           tables=database.get_all_tables(),
                           cafe_name=database.get_setting("cafe_name"),
                           user=session["user"])

@app.route("/tables/add", methods=["POST"])
@login_required
def add_table():
    try:
        database.create_table(request.form["table_number"].strip(),
                              int(request.form["capacity"]))
        flash("Table added.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("tables"))

@app.route("/tables/delete/<int:table_id>", methods=["POST"])
@login_required
def delete_table(table_id):
    database.delete_table(table_id)
    flash("Table deleted.", "success")
    return redirect(url_for("tables"))

@app.route("/tables/status/<int:table_id>", methods=["POST"])
@login_required
def set_table_status(table_id):
    database.update_table_status(table_id, request.form["status"])
    return redirect(url_for("tables"))


# ── Orders ─────────────────────────────────────────────────────────────────────
@app.route("/orders")
@login_required
def orders():
    from datetime import date
    start = request.args.get("start", date.today().strftime("%Y-%m-%d"))
    end = request.args.get("end", date.today().strftime("%Y-%m-%d"))
    status_filter = request.args.get("status", "")
    all_orders = database.get_orders_by_date_range(start, end, status=status_filter or None)
    # Attach item counts
    for o in all_orders:
        o["item_count"] = database.get_order_item_count(o["id"])
    return render_template("orders.html",
                           orders=all_orders,
                           start=start, end=end,
                           status_filter=status_filter,
                           currency=database.get_setting("currency_symbol", "KSh"),
                           cafe_name=database.get_setting("cafe_name"),
                           user=session["user"])


# ── POS — Table Map ────────────────────────────────────────────────────────────
@app.route("/pos")
@login_required
def pos():
    tables = database.get_all_tables()
    for t in tables:
        t["open_order"] = database.get_open_order_for_table(t["id"])
    return render_template("pos_tables.html",
                           tables=tables,
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           user=session["user"])


@app.route("/pos/new-order", methods=["POST"])
@login_required
def pos_new_order():
    table_id = request.form.get("table_id") or None
    if table_id:
        table_id = int(table_id)
        existing = database.get_open_order_for_table(table_id)
        if existing:
            return redirect(url_for("pos_order", order_id=existing["id"]))
    else:
        existing = database.get_open_takeaway_order(session["user"]["id"])
        if existing:
            return redirect(url_for("pos_order", order_id=existing["id"]))
    order_id = database.create_order(session["user"]["id"], table_id)
    return redirect(url_for("pos_order", order_id=order_id))


@app.route("/pos/order/<int:order_id>")
@login_required
def pos_order(order_id):
    data = database.get_order_with_items(order_id)
    if not data:
        flash("Order not found.", "error")
        return redirect(url_for("pos"))
    if data["order"]["status"] not in ("open", "ready"):
        return redirect(url_for("receipt", order_id=order_id))
    categories = database.get_categories()
    all_items = [i for i in database.get_all_items() if i["is_available"]]
    return render_template("pos_order.html",
                           order=data["order"],
                           order_items=data["items"],
                           categories=categories,
                           items=all_items,
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           tax_rate=database.get_setting("tax_rate", "16"),
                           user=session["user"])


@app.route("/pos/order/<int:order_id>/void", methods=["POST"])
@login_required
def pos_void_order(order_id):
    if session["user"]["role"] != "admin":
        flash("Only admins can void orders.", "error")
        return redirect(url_for("pos_order", order_id=order_id))
    database.void_order(order_id)
    flash("Order voided.", "success")
    return redirect(url_for("pos"))


@app.route("/pos/order/<int:order_id>/pay", methods=["GET", "POST"])
@login_required
def pos_pay(order_id):
    data = database.get_order_with_items(order_id)
    if not data:
        flash("Order not found.", "error")
        return redirect(url_for("pos"))
    if data["order"]["status"] not in ("open", "ready"):
        return redirect(url_for("receipt", order_id=order_id))
    if request.method == "POST":
        method = request.form["payment_method"]
        reference = request.form.get("payment_reference", "").strip()
        tendered = float(request.form.get("amount_tendered", 0) or 0)
        database.finalize_order(order_id, method, reference, tendered)
        return redirect(url_for("receipt", order_id=order_id))
    return render_template("pos_pay.html",
                           order=data["order"],
                           order_items=data["items"],
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           user=session["user"])


@app.route("/receipt/<int:order_id>")
@login_required
def receipt(order_id):
    data = database.get_order_with_items(order_id)
    if not data:
        flash("Receipt not found.", "error")
        return redirect(url_for("pos"))
    return render_template("receipt.html",
                           order=data["order"],
                           order_items=data["items"],
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           receipt_footer=database.get_setting("receipt_footer", "Thank you for dining with us!"),
                           receipt_header=database.get_setting("receipt_header", ""),
                           address=database.get_setting("address", ""),
                           phone=database.get_setting("phone", ""),
                           kra_pin=database.get_setting("kra_pin", ""),
                           tax_rate=database.get_setting("tax_rate", "16"),
                           user=session["user"])


# ── Kitchen Display ────────────────────────────────────────────────────────────
@app.route("/kitchen")
@login_required
def kitchen():
    orders = database.get_open_orders_with_items()
    return render_template("kitchen.html",
                           orders=orders,
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           user=session["user"])


@app.route("/kitchen/bump/<int:order_id>", methods=["POST"])
@login_required
def kitchen_bump(order_id):
    database.bump_order(order_id)
    return redirect(url_for("kitchen"))


# ── Void from Orders page ──────────────────────────────────────────────────────
@app.route("/orders/void/<int:order_id>", methods=["POST"])
@admin_required
def orders_void(order_id):
    database.void_order(order_id)
    flash("Order voided.", "success")
    # Preserve date/status filters in redirect
    start = request.form.get("start", "")
    end = request.form.get("end", "")
    status = request.form.get("status", "")
    return redirect(url_for("orders", start=start, end=end, status=status))


# ── POS JSON API ───────────────────────────────────────────────────────────────
@app.route("/api/order/<int:order_id>")
@login_required
def api_get_order(order_id):
    data = database.get_order_with_items(order_id)
    if not data:
        return jsonify({"error": "Not found"}), 404
    return jsonify(data)


@app.route("/api/order/<int:order_id>/add-item", methods=["POST"])
@login_required
def api_add_item(order_id):
    item_id = int(request.json["item_id"])
    item = database.get_item_by_id(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    if not item.get("is_available"):
        return jsonify({"error": "Item is not available"}), 400
    data = database.get_order_with_items(order_id)
    if not data or data["order"]["status"] not in ("open", "ready"):
        return jsonify({"error": "Order is not open"}), 400
    database.add_order_item(order_id, item_id, item["name"], item["price"])
    return jsonify(database.get_order_with_items(order_id))


@app.route("/api/order/<int:order_id>/update-item/<int:oi_id>", methods=["POST"])
@login_required
def api_update_item(order_id, oi_id):
    qty = int(request.json["qty"])
    database.update_order_item_qty(oi_id, qty)
    return jsonify(database.get_order_with_items(order_id))


@app.route("/api/order/<int:order_id>/set-discount", methods=["POST"])
@login_required
def api_set_discount(order_id):
    dtype = request.json.get("type", "percent")
    dval = float(request.json.get("value", 0))
    database.set_order_discount(order_id, dtype, dval)
    return jsonify(database.get_order_with_items(order_id))


@app.route("/api/order/<int:order_id>/item-note/<int:oi_id>", methods=["POST"])
@login_required
def api_set_item_note(order_id, oi_id):
    note = request.json.get("note", "").strip()
    database.set_order_item_note(oi_id, note)
    return jsonify(database.get_order_with_items(order_id))


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  QUEENS CAFE — Web Dashboard")
    print("  Open your browser: http://localhost:5000")
    print("  Login: admin / admin123")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
