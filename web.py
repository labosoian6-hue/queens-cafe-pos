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
        login_type = request.form.get("login_type", "admin")
        if login_type == "pin":
            pin = request.form.get("pin", "").strip()
            user = database.verify_pin(pin)
            if user:
                session["user"] = dict(user)
                return redirect(url_for("dashboard"))
            error = "Incorrect PIN. Please try again."
        else:
            user = database.verify_password(
                request.form["username"], request.form["password"]
            )
            if user:
                session["user"] = dict(user)
                return redirect(url_for("dashboard"))
            error = "Invalid username or password."
    cashiers = database.get_active_cashiers()
    return render_template("login.html", error=error,
                           cashiers=cashiers,
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


# ── Settings ── (moved below with extended fields)


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

@app.route("/staff/set-pin/<int:staff_id>", methods=["POST"])
@admin_required
def set_staff_pin(staff_id):
    pin = request.form.get("pin", "").strip()
    if len(pin) < 4:
        flash("PIN must be at least 4 digits.", "error")
        return redirect(url_for("staff"))
    database.set_staff_pin(staff_id, pin)
    flash("PIN updated successfully.", "success")
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
                           discount_threshold=database.get_setting("discount_threshold", "10"),
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


@app.route("/pos/order/<int:order_id>/kitchen-ticket")
@login_required
def kitchen_ticket(order_id):
    data = database.get_order_with_items(order_id)
    if not data:
        return "Order not found", 404
    return render_template("kitchen_ticket.html",
                           order=data["order"],
                           order_items=data["items"],
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           receipt_footer=database.get_setting("receipt_footer", "Thank you for dining with us!"),
                           receipt_header=database.get_setting("receipt_header", ""),
                           address=database.get_setting("address", ""),
                           phone=database.get_setting("phone", ""),
                           till_number=database.get_setting("till_number", ""))


@app.route("/pos/order/<int:order_id>/order-slip")
@login_required
def order_slip(order_id):
    data = database.get_order_with_items(order_id)
    if not data:
        return "Order not found", 404
    return render_template("order_slip.html",
                           order=data["order"],
                           order_items=data["items"],
                           cafe_name=database.get_setting("cafe_name", "QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol", "KSh"),
                           address=database.get_setting("address", ""),
                           phone=database.get_setting("phone", ""),
                           tax_rate=database.get_setting("tax_rate", "16"))


@app.route("/training")
@login_required
def training_manual():
    return render_template("training_manual.html")


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
                           tax_rate=database.get_setting("tax_rate", "16"),
                           till_number=database.get_setting("till_number", ""),
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


# ── Kitchen JSON API ───────────────────────────────────────────────────────────
@app.route("/api/kitchen/orders")
@login_required
def api_kitchen_orders():
    orders = database.get_open_orders_with_items()
    return jsonify({"order_ids": [o["order"]["id"] for o in orders]})


# ── Tables Free API ────────────────────────────────────────────────────────────
@app.route("/api/tables/free")
@login_required
def api_tables_free():
    tables = database.get_all_tables()
    free = [t for t in tables if t["status"] == "free"]
    return jsonify({"tables": free})


# ── Table Transfer ─────────────────────────────────────────────────────────────
@app.route("/pos/order/<int:order_id>/transfer-table", methods=["POST"])
@login_required
def transfer_table(order_id):
    new_table_id = request.form.get("new_table_id")
    if not new_table_id:
        flash("Please select a table.", "error")
        return redirect(url_for("pos_order", order_id=order_id))
    try:
        database.transfer_order_table(order_id, int(new_table_id))
        flash("Table transferred successfully.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("pos_order", order_id=order_id))


# ── Manager PIN API ────────────────────────────────────────────────────────────
@app.route("/api/verify-manager-pin", methods=["POST"])
@login_required
def api_verify_manager_pin():
    pin = request.json.get("pin", "")
    stored = database.get_setting("manager_pin", "")
    if stored and pin == stored:
        return jsonify({"ok": True})
    return jsonify({"ok": False})


# ── Reports CSV Export ─────────────────────────────────────────────────────────
@app.route("/reports/export-csv")
@login_required
def reports_export_csv():
    import csv, io
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    start = request.args.get("start", today)
    end = request.args.get("end", today)
    orders = database.get_orders_by_date_range(start, end, status="paid")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Receipt#","Date","Time","Table","Cashier","Subtotal","Discount","Tax","Total","Payment Method","Reference"])
    for o in orders:
        paid_at = o.get("paid_at","") or ""
        date_part = paid_at[:10] if paid_at else ""
        time_part = paid_at[11:16] if len(paid_at) > 10 else ""
        writer.writerow([
            o.get("receipt_number",""),
            date_part,
            time_part,
            o.get("table_number","") or "Takeaway",
            o.get("cashier_name",""),
            "{:.2f}".format(o.get("subtotal",0) or 0),
            "{:.2f}".format(o.get("discount_amount",0) or 0),
            "{:.2f}".format(o.get("tax_amount",0) or 0),
            "{:.2f}".format(o.get("total",0) or 0),
            o.get("payment_method",""),
            o.get("payment_reference","")
        ])
    csv_data = output.getvalue()
    from flask import Response
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=transactions_{start}_to_{end}.csv"}
    )


# ── Z-Report / Shift Report ────────────────────────────────────────────────────
@app.route("/reports/zreport")
@login_required
def zreport():
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    summary = database.get_daily_summary(today)
    top_items = database.get_top_items(today, limit=10)
    by_cat = database.get_sales_by_category(today)
    all_orders = database.get_orders_by_date_range(today, today)
    paid_orders = [o for o in all_orders if o["status"] == "paid"]
    voided_orders = [o for o in all_orders if o["status"] == "voided"]
    # VAT collected
    vat_collected = sum(o.get("tax_amount",0) or 0 for o in paid_orders)
    return render_template("zreport.html",
                           summary=summary,
                           top_items=top_items,
                           by_cat=by_cat,
                           paid_orders=paid_orders,
                           voided_orders=voided_orders,
                           vat_collected=vat_collected,
                           today=today,
                           currency=database.get_setting("currency_symbol","KSh"),
                           cafe_name=database.get_setting("cafe_name","QUEENS CAFE"),
                           user=session["user"])


# ── Modifiers Management ───────────────────────────────────────────────────────
@app.route("/menu/modifiers")
@login_required
def menu_modifiers():
    items = database.get_all_items()
    modifiers = database.get_all_modifiers()
    return render_template("modifiers.html",
                           items=items,
                           modifiers=modifiers,
                           cafe_name=database.get_setting("cafe_name","QUEENS CAFE"),
                           user=session["user"])

@app.route("/menu/modifiers/add", methods=["POST"])
@login_required
def add_modifier():
    try:
        database.create_modifier(
            int(request.form["menu_item_id"]),
            request.form["name"].strip(),
            float(request.form.get("price_delta",0) or 0)
        )
        flash("Modifier added.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("menu_modifiers"))

@app.route("/menu/modifiers/delete/<int:mod_id>", methods=["POST"])
@login_required
def delete_modifier(mod_id):
    database.delete_modifier(mod_id)
    flash("Modifier deleted.", "success")
    return redirect(url_for("menu_modifiers"))

@app.route("/menu/modifiers/toggle/<int:mod_id>", methods=["POST"])
@login_required
def toggle_modifier(mod_id):
    database.toggle_modifier(mod_id)
    return redirect(url_for("menu_modifiers"))

@app.route("/api/item/<int:item_id>/modifiers")
@login_required
def api_item_modifiers(item_id):
    mods = database.get_modifiers_for_item(item_id)
    return jsonify({"modifiers": mods})

@app.route("/api/order/<int:order_id>/add-item-with-modifiers", methods=["POST"])
@login_required
def api_add_item_with_modifiers(order_id):
    data = request.json
    item_id = int(data["item_id"])
    modifier_ids = data.get("modifier_ids", [])
    item = database.get_item_by_id(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    if not item.get("is_available"):
        return jsonify({"error": "Item not available"}), 400
    order_data = database.get_order_with_items(order_id)
    if not order_data or order_data["order"]["status"] not in ("open","ready"):
        return jsonify({"error": "Order not open"}), 400
    # Calculate total price with modifiers
    mods = database.get_modifiers_for_item(item_id)
    selected_mods = [m for m in mods if m["id"] in modifier_ids]
    extra = sum(m["price_delta"] for m in selected_mods)
    unit_price = item["price"] + extra
    # Add item with modifier suffix in name
    mod_names = ", ".join(m["name"] for m in selected_mods)
    display_name = item["name"] + (" [" + mod_names + "]" if mod_names else "")
    oi_id = database.add_order_item_raw(order_id, item_id, display_name, unit_price)
    if selected_mods:
        database.add_order_item_modifiers(oi_id, selected_mods)
    return jsonify(database.get_order_with_items(order_id))


# ── Split Bill ─────────────────────────────────────────────────────────────────
@app.route("/pos/order/<int:order_id>/split", methods=["GET"])
@login_required
def split_bill_page(order_id):
    data = database.get_order_with_items(order_id)
    if not data:
        flash("Order not found.", "error")
        return redirect(url_for("pos"))
    if data["order"]["status"] not in ("open","ready"):
        flash("Order is not open.", "error")
        return redirect(url_for("pos"))
    return render_template("split_bill.html",
                           order=data["order"],
                           order_items=data["items"],
                           cafe_name=database.get_setting("cafe_name","QUEENS CAFE"),
                           currency=database.get_setting("currency_symbol","KSh"),
                           tax_rate=database.get_setting("tax_rate","16"),
                           user=session["user"])

@app.route("/pos/order/<int:order_id>/split", methods=["POST"])
@login_required
def split_bill(order_id):
    item_ids = request.form.getlist("item_ids[]")
    if not item_ids:
        flash("Please select at least one item for the split.", "error")
        return redirect(url_for("split_bill_page", order_id=order_id))
    item_ids = [int(i) for i in item_ids]
    try:
        new_order_id = database.split_order(order_id, item_ids, session["user"]["id"])
        return redirect(url_for("pos_pay", order_id=new_order_id))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("split_bill_page", order_id=order_id))


# ── Settings (updated with manager_pin & discount_threshold) ────────────────────
# Override the settings route to include new fields
@app.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        for key in ["cafe_name", "tax_rate", "currency_symbol", "receipt_footer",
                    "address", "phone", "receipt_header",
                    "manager_pin", "discount_threshold", "till_number"]:
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
                           receipt_header=database.get_setting("receipt_header"),
                           manager_pin=database.get_setting("manager_pin",""),
                           discount_threshold=database.get_setting("discount_threshold","10"),
                           till_number=database.get_setting("till_number",""),
                           user=session["user"])


if __name__ == "__main__":
    import socket
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except:
        local_ip = "YOUR-PC-IP"
    print("\n" + "="*50)
    print("  QUEENS CAFE — Web Dashboard")
    print(f"  Local:   http://localhost:5000")
    print(f"  Network: http://{local_ip}:5000")
    print("  Login: admin / admin123")
    print("="*50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
