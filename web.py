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
    return render_template("dashboard.html",
                           summary=summary,
                           top_items=top_items,
                           by_cat=by_cat,
                           recent_orders=recent_orders,
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
        for key in ["cafe_name", "tax_rate", "currency_symbol", "receipt_footer"]:
            database.set_setting(key, request.form.get(key, "").strip())
        flash("Settings saved successfully.", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html",
                           cafe_name=database.get_setting("cafe_name"),
                           tax_rate=database.get_setting("tax_rate"),
                           currency_symbol=database.get_setting("currency_symbol"),
                           receipt_footer=database.get_setting("receipt_footer"),
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


# ── Reports ────────────────────────────────────────────────────────────────────
@app.route("/reports")
@login_required
def reports():
    from datetime import date
    selected = request.args.get("date", date.today().strftime("%Y-%m-%d"))
    summary = database.get_daily_summary(selected)
    top_items = database.get_top_items(selected, limit=10)
    by_cat = database.get_sales_by_category(selected)
    orders = database.get_orders_by_date_range(selected, selected, status="paid")
    return render_template("reports.html",
                           summary=summary,
                           top_items=top_items,
                           by_cat=by_cat,
                           orders=orders,
                           selected_date=selected,
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
    all_orders = database.get_orders_by_date_range(start, end)
    return render_template("orders.html",
                           orders=all_orders,
                           start=start, end=end,
                           currency=database.get_setting("currency_symbol", "KSh"),
                           cafe_name=database.get_setting("cafe_name"),
                           user=session["user"])


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  QUEENS CAFE — Web Dashboard")
    print("  Open your browser: http://localhost:5000")
    print("  Login: admin / admin123")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
