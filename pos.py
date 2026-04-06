"""
pos.py - All GUI screens for CAFE POS System
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import os, csv, tempfile

import database
import auth
import printer

# ── Theme ──────────────────────────────────────────────────────────────────────
BG      = "#1a1a2e"
BG2     = "#16213e"
BG3     = "#0f3460"
PANEL   = "#1e2a45"
ACCENT  = "#e94560"
GREEN   = "#4dbd74"
YELLOW  = "#f4a261"
ORANGE  = "#e76f51"
TEXT    = "#eaeaea"
SUBTEXT = "#a0a4c8"
FONT    = "Courier New"
FONTSANS= "Segoe UI"

def _style():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("S.Treeview", background=BG3, foreground=TEXT,
                fieldbackground=BG3, rowheight=28, font=(FONTSANS, 10))
    s.configure("S.Treeview.Heading", background=BG2, foreground=ACCENT,
                font=(FONTSANS, 10, "bold"), relief="flat")
    s.map("S.Treeview", background=[("selected", "#3d4f6b")])
    s.configure("TNotebook", background=BG2, borderwidth=0)
    s.configure("TNotebook.Tab", background=BG3, foreground=SUBTEXT,
                font=(FONTSANS, 10, "bold"), padding=[12, 6])
    s.map("TNotebook.Tab", background=[("selected", ACCENT)],
          foreground=[("selected", TEXT)])
    s.configure("TScrollbar", background=BG3, troughcolor=BG2, arrowcolor=TEXT)


def btn(parent, text, cmd, color=ACCENT, fg=TEXT, size=10, **kw):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=fg, relief="flat", cursor="hand2",
                  font=(FONTSANS, size, "bold"), padx=8, pady=5,
                  activebackground=color, activeforeground=fg, **kw)
    return b


def lbl(parent, text, size=10, bold=False, color=TEXT, **kw):
    w = "bold" if bold else "normal"
    return tk.Label(parent, text=text, font=(FONTSANS, size, w),
                    bg=parent["bg"], fg=color, **kw)


def ent(parent, width=20, **kw):
    return tk.Entry(parent, width=width, bg=BG3, fg=TEXT,
                    insertbackground=ACCENT, relief="flat",
                    font=(FONTSANS, 11), bd=3, **kw)


def sep(parent):
    return tk.Frame(parent, bg=ACCENT, height=1)


# ══════════════════════════════════════════════════════════════════════════════
# NAV BAR
# ══════════════════════════════════════════════════════════════════════════════
class NavBar(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG2, pady=4)
        self.app = app
        user = auth.Session.get_current_user()

        lbl(self, database.get_setting("cafe_name", "CAFE POS"),
            size=14, bold=True, color=ACCENT).pack(side="left", padx=16)

        nav_btns = [("POS", "pos"), ("Menu", "menu"), ("Tables", "tables"),
                    ("Orders", "orders"), ("Reports", "reports")]
        if auth.Session.is_admin():
            nav_btns += [("Staff", "staff"), ("Settings", "settings")]

        for label_text, screen in nav_btns:
            btn(self, label_text, lambda s=screen: app.show_screen(s),
                color=BG3, size=9).pack(side="left", padx=2)

        right = tk.Frame(self, bg=BG2)
        right.pack(side="right", padx=12)
        lbl(right, f"{user['full_name']}  [{user['role'].upper()}]",
            size=9, color=SUBTEXT).pack(side="left", padx=8)
        btn(right, "Logout", self._logout, color=ORANGE, size=9).pack(side="left", padx=4)
        if auth.Session.is_admin():
            btn(right, "Exit App", self._exit_app, color=ACCENT, size=9).pack(side="left", padx=4)

    def _logout(self):
        if messagebox.askyesno("Logout", "Log out of the system?"):
            auth.Session.logout()
            self.app.show_screen("login")

    def _exit_app(self):
        if messagebox.askyesno("Exit", "Close the POS system?"):
            self.app._exit_app()


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class LoginScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)

        tk.Label(self, text=database.get_setting("cafe_name", "CAFE POS"),
                 font=(FONT, 28, "bold"), bg=BG, fg=ACCENT).pack(pady=(70, 6))
        tk.Label(self, text="Point of Sale & Management System",
                 font=(FONTSANS, 12), bg=BG, fg=SUBTEXT).pack(pady=(0, 40))

        card = tk.Frame(self, bg=BG2, padx=40, pady=32)
        card.pack(padx=80)

        lbl(card, "Username", color=SUBTEXT).pack(anchor="w")
        self.user_var = tk.StringVar()
        ent(card, width=30, textvariable=self.user_var).pack(fill="x", pady=(2, 12))

        lbl(card, "Password", color=SUBTEXT).pack(anchor="w")
        self.pass_var = tk.StringVar()
        pw = ent(card, width=30, textvariable=self.pass_var, show="●")
        pw.pack(fill="x", pady=(2, 20))
        pw.bind("<Return>", lambda e: self._login())

        btn(card, "  LOG IN  ▶", self._login, size=12).pack(fill="x", ipady=6)
        self.err_lbl = lbl(card, "", color=ACCENT, size=9)
        self.err_lbl.pack(pady=(8, 0))

    def _login(self):
        try:
            auth.Session.login(self.user_var.get().strip(), self.pass_var.get())
            self.app.show_screen("pos")
        except auth.AuthError as e:
            self.err_lbl.config(text=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# POS SCREEN
# ══════════════════════════════════════════════════════════════════════════════
class POSScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)

        NavBar(self, app).pack(fill="x")
        sep(self).pack(fill="x")

        self.order_id = None
        self.current_table_id = None
        self.current_table_name = "Takeaway"

        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True)

        # Left panel — tables
        self._build_table_panel(content)

        # Center — menu
        self._build_menu_panel(content)

        # Right — cart
        self._build_cart_panel(content)

        self._refresh_tables()
        self._load_menu()

    # ── Table Panel ────────────────────────────────────────────────────────────
    def _build_table_panel(self, parent):
        self.table_frame = tk.Frame(parent, bg=BG2, width=140)
        self.table_frame.pack(side="left", fill="y", padx=(4, 2), pady=4)
        self.table_frame.pack_propagate(False)

        lbl(self.table_frame, "TABLES", size=9, bold=True, color=SUBTEXT).pack(pady=(8, 4))

        btn(self.table_frame, "Takeaway", self._select_takeaway,
            color=BG3, size=9).pack(fill="x", padx=6, pady=2)

        self.tables_inner = tk.Frame(self.table_frame, bg=BG2)
        self.tables_inner.pack(fill="both", expand=True, padx=6, pady=4)

    def _refresh_tables(self):
        for w in self.tables_inner.winfo_children():
            w.destroy()
        for t in database.get_all_tables():
            color = GREEN if t["status"] == "free" else YELLOW if t["status"] == "occupied" else ORANGE
            btn(self.tables_inner, t["table_number"],
                lambda tid=t["id"], tnum=t["table_number"], st=t["status"]: self._toggle_table(tid, tnum, st),
                color=color, fg=BG2, size=9).pack(fill="x", pady=1)

    def _select_takeaway(self):
        self.current_table_id = None
        self.current_table_name = "Takeaway"
        user = auth.Session.get_current_user()
        existing = database.get_open_takeaway_order(user["id"])
        if existing:
            self.order_id = existing["id"]
        else:
            self.order_id = database.create_order(user["id"], None)
        self._refresh_cart()

    def _toggle_table(self, table_id, table_name, current_status):
        if current_status == "free":
            # First click: mark occupied and start order
            self.current_table_id = table_id
            self.current_table_name = table_name
            existing = database.get_open_order_for_table(table_id)
            if existing:
                self.order_id = existing["id"]
            else:
                user = auth.Session.get_current_user()
                self.order_id = database.create_order(user["id"], table_id)
            self._refresh_tables()
            self._refresh_cart()
        else:
            # Second click (occupied/reserved): load existing order into cart
            self.current_table_id = table_id
            self.current_table_name = table_name
            existing = database.get_open_order_for_table(table_id)
            if existing:
                self.order_id = existing["id"]
            else:
                # No open order — reset to free
                database.update_table_status(table_id, "free")
            self._refresh_tables()
            self._refresh_cart()

    # ── Menu Panel ─────────────────────────────────────────────────────────────
    def _build_menu_panel(self, parent):
        center = tk.Frame(parent, bg=BG)
        center.pack(side="left", fill="both", expand=True, padx=2, pady=4)

        top = tk.Frame(center, bg=BG)
        top.pack(fill="x", pady=(0, 4))
        lbl(top, "MENU", size=9, bold=True, color=SUBTEXT).pack(side="left", padx=6)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._on_search())
        ent(top, width=22, textvariable=self.search_var).pack(side="left", padx=4)
        lbl(top, "🔍", color=SUBTEXT).pack(side="left")

        self.notebook = ttk.Notebook(center, style="TNotebook")
        self.notebook.pack(fill="both", expand=True)
        self.search_frame = None

    def _load_menu(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        for cat in database.get_categories():
            items = database.get_items_by_category(cat["id"])
            frame = tk.Frame(self.notebook, bg=BG)
            self.notebook.add(frame, text=cat["name"])
            self._populate_item_grid(frame, items)

    def _populate_item_grid(self, frame, items):
        for w in frame.winfo_children():
            w.destroy()

        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        cols = 3
        for i, item in enumerate(items):
            r, c = divmod(i, cols)
            color = PANEL if item.get("is_available", 1) else BG3
            f = tk.Frame(inner, bg=color, padx=4, pady=4, relief="flat", bd=1)
            f.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            inner.columnconfigure(c, weight=1)

            currency = database.get_setting("currency_symbol", "KSh")
            name_lbl = tk.Label(f, text=item["name"], font=(FONTSANS, 10, "bold"),
                                bg=color, fg=TEXT, wraplength=130, justify="center")
            name_lbl.pack(pady=(4, 2))
            tk.Label(f, text=f"{currency} {item['price']:,.0f}",
                     font=(FONTSANS, 11, "bold"), bg=color, fg=YELLOW).pack()

            if item.get("is_available", 1):
                b = tk.Button(f, text="Add +", bg=ACCENT, fg=TEXT, relief="flat",
                              font=(FONTSANS, 9, "bold"), cursor="hand2",
                              command=lambda it=item: self._add_item(it))
                b.pack(pady=(4, 2), fill="x")
            else:
                tk.Label(f, text="Unavailable", fg=ORANGE, bg=color,
                         font=(FONTSANS, 8)).pack()

    def _on_search(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self._load_menu()
            return
        all_items = database.get_all_items()
        results = [i for i in all_items if query in i["name"].lower()]
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        frame = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(frame, text=f'Search: "{query}"')
        self._populate_item_grid(frame, results)

    def _add_item(self, item):
        if not self.order_id:
            self._select_takeaway()
        database.add_order_item(
            self.order_id, item["id"], item["name"], item["price"]
        )
        self._refresh_cart()

    # ── Cart Panel ─────────────────────────────────────────────────────────────
    def _build_cart_panel(self, parent):
        cart_frame = tk.Frame(parent, bg=BG2, width=320)
        cart_frame.pack(side="right", fill="y", padx=(2, 4), pady=4)
        cart_frame.pack_propagate(False)
        self.cart_frame = cart_frame

        self.cart_title = lbl(cart_frame, "CART — Takeaway", size=10, bold=True, color=ACCENT)
        self.cart_title.pack(pady=(8, 2), padx=8, anchor="w")
        sep(cart_frame).pack(fill="x", padx=4, pady=2)

        # Treeview
        cols = ("Item", "Qty", "Price", "Total")
        widths = (130, 40, 60, 70)
        frame, self.cart_tree = self._make_tree(cart_frame, cols, widths, height=10)
        frame.pack(fill="both", expand=True, padx=4, pady=2)

        # Qty controls
        ctrl = tk.Frame(cart_frame, bg=BG2)
        ctrl.pack(fill="x", padx=4, pady=2)
        btn(ctrl, "−", self._dec_qty, color=BG3, size=11).pack(side="left", padx=2)
        btn(ctrl, "+", self._inc_qty, color=BG3, size=11).pack(side="left", padx=2)
        btn(ctrl, "Remove", self._remove_item, color=ORANGE, size=9).pack(side="left", padx=2)
        btn(ctrl, "Clear", self._clear_order, color=ACCENT, size=9).pack(side="right", padx=2)

        sep(cart_frame).pack(fill="x", padx=4, pady=4)

        # Discount
        disc_row = tk.Frame(cart_frame, bg=BG2)
        disc_row.pack(fill="x", padx=8, pady=2)
        lbl(disc_row, "Discount:", size=9, color=SUBTEXT).pack(side="left")
        self.disc_type = tk.StringVar(value="percent")
        tk.Radiobutton(disc_row, text="%", variable=self.disc_type, value="percent",
                       bg=BG2, fg=TEXT, selectcolor=BG3,
                       font=(FONTSANS, 9)).pack(side="left", padx=4)
        tk.Radiobutton(disc_row, text="Fixed", variable=self.disc_type, value="fixed",
                       bg=BG2, fg=TEXT, selectcolor=BG3,
                       font=(FONTSANS, 9)).pack(side="left")
        self.disc_var = tk.StringVar(value="0")
        ent(disc_row, width=6, textvariable=self.disc_var).pack(side="left", padx=4)
        btn(disc_row, "Apply", self._apply_discount, color=BG3, size=9).pack(side="left")

        sep(cart_frame).pack(fill="x", padx=4, pady=4)

        # Totals
        totals = tk.Frame(cart_frame, bg=BG2)
        totals.pack(fill="x", padx=10, pady=2)
        currency = database.get_setting("currency_symbol", "KSh")

        def tot_row(label_text, big=False):
            row = tk.Frame(totals, bg=BG2)
            row.pack(fill="x", pady=1)
            size = 11 if big else 9
            color = YELLOW if big else TEXT
            lbl(row, label_text, size=size, bold=big, color=SUBTEXT).pack(side="left")
            l = lbl(row, "0.00", size=size, bold=big, color=color)
            l.pack(side="right")
            return l

        self.sub_lbl   = tot_row(f"Subtotal ({currency})")
        self.disc_lbl  = tot_row("Discount")
        self.tax_lbl   = tot_row(f"Tax ({database.get_setting('tax_rate', '16')}%)")
        sep(totals).pack(fill="x", pady=2)
        self.total_lbl = tot_row(f"TOTAL ({currency})", big=True)

        sep(cart_frame).pack(fill="x", padx=4, pady=4)

        # Payment buttons
        pay = tk.Frame(cart_frame, bg=BG2)
        pay.pack(fill="x", padx=4, pady=2)
        btn(pay, "Cash", lambda: self._pay("cash"), color=GREEN, size=10).pack(side="left", expand=True, fill="x", padx=2)
        btn(pay, "Card", lambda: self._pay("card"), color=BG3, size=10).pack(side="left", expand=True, fill="x", padx=2)
        btn(pay, "M-Pesa", lambda: self._pay("mpesa"), color="#00a651", size=10).pack(side="left", expand=True, fill="x", padx=2)

        bottom = tk.Frame(cart_frame, bg=BG2)
        bottom.pack(fill="x", padx=4, pady=(2, 8))
        btn(bottom, "Print Receipt", self._print_last_receipt, color=SUBTEXT, fg=BG, size=9).pack(side="left", padx=2)
        if auth.Session.is_admin():
            btn(bottom, "Void Order", self._void_order, color=ACCENT, size=9).pack(side="right", padx=2)

        self.last_paid_order_id = None

    def _make_tree(self, parent, cols, widths, height=10):
        f = tk.Frame(parent, bg=BG2)
        tree = ttk.Treeview(f, columns=cols, show="headings",
                            height=height, style="S.Treeview")
        vsb = ttk.Scrollbar(f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="w")
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return f, tree

    def _refresh_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        if not self.order_id:
            self.cart_title.config(text="CART — No order selected")
            for lbl_w in (self.sub_lbl, self.disc_lbl, self.tax_lbl, self.total_lbl):
                lbl_w.config(text="0.00")
            return

        data = database.get_order_with_items(self.order_id)
        if not data:
            return

        order = data["order"]
        self.cart_title.config(text=f"CART — {self.current_table_name}  #{order['receipt_number']}")

        currency = database.get_setting("currency_symbol", "KSh")
        for item in data["items"]:
            self.cart_tree.insert("", "end", iid=str(item["id"]),
                                  values=(item["item_name"], item["quantity"],
                                          f"{item['unit_price']:,.0f}",
                                          f"{item['line_total']:,.0f}"))

        self.sub_lbl.config(text=f"{order['subtotal']:,.2f}")
        self.disc_lbl.config(text=f"-{order['discount_amount']:,.2f}")
        self.tax_lbl.config(text=f"{order['tax_amount']:,.2f}")
        self.total_lbl.config(text=f"{order['total']:,.2f}")

    def _dec_qty(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        oi_id = int(sel[0])
        vals = self.cart_tree.item(sel[0])["values"]
        database.update_order_item_qty(oi_id, int(vals[1]) - 1)
        self._refresh_cart()

    def _inc_qty(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        oi_id = int(sel[0])
        vals = self.cart_tree.item(sel[0])["values"]
        database.update_order_item_qty(oi_id, int(vals[1]) + 1)
        self._refresh_cart()

    def _remove_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        database.remove_order_item(int(sel[0]))
        self._refresh_cart()

    def _clear_order(self):
        if not self.order_id:
            return
        if messagebox.askyesno("Clear Cart", "Remove all items from cart?"):
            database.void_order(self.order_id)
            self.order_id = None
            self._refresh_tables()
            self._refresh_cart()

    def _apply_discount(self):
        if not self.order_id:
            return
        try:
            val = float(self.disc_var.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number for discount.")
            return
        database.set_order_discount(self.order_id, self.disc_type.get(), val)
        self._refresh_cart()

    def _pay(self, method):
        if not self.order_id:
            messagebox.showwarning("No Order", "Select a table or takeaway first.")
            return
        data = database.get_order_with_items(self.order_id)
        if not data or not data["items"]:
            messagebox.showwarning("Empty Cart", "Add items before payment.")
            return
        order = data["order"]
        if order["total"] <= 0:
            messagebox.showwarning("Zero Total", "Order total is zero.")
            return
        dlg = PaymentDialog(self, method, order["total"])
        self.wait_window(dlg)
        if dlg.confirmed:
            database.finalize_order(
                self.order_id, method,
                dlg.reference, dlg.tendered
            )
            self.last_paid_order_id = self.order_id
            self.order_id = None
            self._refresh_tables()
            self._refresh_cart()
            ReceiptWindow(self, self.last_paid_order_id)

    def _print_last_receipt(self):
        if self.last_paid_order_id:
            ReceiptWindow(self, self.last_paid_order_id)
        else:
            messagebox.showinfo("No Receipt", "No recent receipt to print.")

    def _void_order(self):
        if not self.order_id:
            return
        if messagebox.askyesno("Void Order", "Void this order? This cannot be undone."):
            database.void_order(self.order_id)
            self.order_id = None
            self._refresh_tables()
            self._refresh_cart()


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, method, total):
        super().__init__(parent)
        self.confirmed = False
        self.reference = ""
        self.tendered = 0.0
        self.total = total
        self.method = method

        currency = database.get_setting("currency_symbol", "KSh")
        self.title(f"Payment — {method.upper()}")
        self.configure(bg=BG2)
        self.resizable(False, False)
        self.grab_set()

        lbl(self, f"Total: {currency} {total:,.2f}", size=16, bold=True,
            color=YELLOW).pack(pady=(20, 10), padx=30)
        sep(self).pack(fill="x", padx=10, pady=6)

        frm = tk.Frame(self, bg=BG2, padx=24, pady=10)
        frm.pack(fill="x")

        if method == "cash":
            lbl(frm, "Amount Tendered:", color=SUBTEXT).pack(anchor="w")
            self.tend_var = tk.StringVar()
            self.tend_var.trace_add("write", self._calc_change)
            ent(frm, width=20, textvariable=self.tend_var).pack(fill="x", pady=(2, 8))
            self.change_lbl = lbl(frm, f"Change: {currency} 0.00", size=12, bold=True, color=GREEN)
            self.change_lbl.pack(pady=4)

        elif method == "card":
            lbl(frm, "Card Last 4 Digits:", color=SUBTEXT).pack(anchor="w")
            self.ref_var = tk.StringVar()
            ent(frm, width=20, textvariable=self.ref_var).pack(fill="x", pady=(2, 8))

        elif method == "mpesa":
            lbl(frm, "M-Pesa Reference Code:", color=SUBTEXT).pack(anchor="w")
            self.ref_var = tk.StringVar()
            ent(frm, width=20, textvariable=self.ref_var).pack(fill="x", pady=(2, 8))

        sep(self).pack(fill="x", padx=10, pady=6)

        row = tk.Frame(self, bg=BG2)
        row.pack(pady=(4, 20), padx=24)
        btn(row, "Confirm Payment", self._confirm, color=GREEN, size=11).pack(side="left", padx=6, ipady=4)
        btn(row, "Cancel", self.destroy, color=ACCENT, size=11).pack(side="left", padx=6, ipady=4)

        self.geometry(f"360x{320 if method == 'cash' else 260}+{parent.winfo_rootx()+200}+{parent.winfo_rooty()+100}")

    def _calc_change(self, *_):
        currency = database.get_setting("currency_symbol", "KSh")
        try:
            t = float(self.tend_var.get())
            change = max(0, t - self.total)
            self.change_lbl.config(text=f"Change: {currency} {change:,.2f}")
        except ValueError:
            self.change_lbl.config(text=f"Change: {currency} 0.00")

    def _confirm(self):
        if self.method == "cash":
            try:
                self.tendered = float(self.tend_var.get())
                if self.tendered < self.total:
                    messagebox.showerror("Insufficient", "Amount tendered is less than total.", parent=self)
                    return
            except ValueError:
                messagebox.showerror("Error", "Enter a valid amount.", parent=self)
                return
        else:
            ref = self.ref_var.get().strip()
            if not ref:
                messagebox.showerror("Error", f"Enter {self.method.upper()} reference.", parent=self)
                return
            self.reference = ref
            self.tendered = self.total
        self.confirmed = True
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# RECEIPT WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class ReceiptWindow(tk.Toplevel):
    def __init__(self, parent, order_id):
        super().__init__(parent)
        self.title("Receipt")
        self.configure(bg=BG2)
        self.resizable(False, False)

        data = database.get_order_with_items(order_id)
        if not data:
            lbl(self, "Order not found.", color=ACCENT).pack(pady=20)
            return

        self._order_data = data
        order = data["order"]
        items = data["items"]
        cafe = database.get_setting("cafe_name", "CAFE POS")
        currency = database.get_setting("currency_symbol", "KSh")
        footer = database.get_setting("receipt_footer", "")
        tax_rate = database.get_setting("tax_rate", "16")
        table = order.get("table_number") or "Takeaway"

        lines = [
            f"{'='*40}",
            f"{cafe:^40}",
            f"{'='*40}",
            f"Receipt : {order['receipt_number']}",
            f"Date    : {order.get('paid_at', order['created_at'])[:16]}",
            f"Cashier : {order['cashier_name']}",
            f"Table   : {table}",
            f"{'─'*40}",
            f"{'Item':<22}{'Qty':>4}{'Price':>7}{'Total':>7}",
            f"{'─'*40}",
        ]
        for it in items:
            name = it["item_name"][:20]
            lines.append(f"{name:<22}{it['quantity']:>4}{it['unit_price']:>7.0f}{it['line_total']:>7.0f}")

        lines += [
            f"{'─'*40}",
            f"{'Subtotal':<28}{order['subtotal']:>10,.2f}",
            f"{'Discount':<28}-{order['discount_amount']:>9,.2f}",
            f"{'Tax (' + tax_rate + '%)':<28}{order['tax_amount']:>10,.2f}",
            f"{'─'*40}",
            f"{'TOTAL ' + currency:<28}{order['total']:>10,.2f}",
            f"{'─'*40}",
            f"Payment : {order['payment_method'].upper()}",
        ]
        if order.get("payment_reference"):
            lines.append(f"Ref     : {order['payment_reference']}")
        if order["payment_method"] == "cash":
            lines += [
                f"Tendered: {currency} {order['amount_tendered']:,.2f}",
                f"Change  : {currency} {order['change_given']:,.2f}",
            ]
        lines += [
            f"{'='*40}",
            f"{footer:^40}",
            f"{'='*40}",
        ]

        receipt_text = "\n".join(lines)

        # Two-column layout: customer receipt | kitchen receipt
        cols_frame = tk.Frame(self, bg=BG2)
        cols_frame.pack(padx=10, pady=10)

        # Customer receipt column
        left_col = tk.Frame(cols_frame, bg=BG2)
        left_col.pack(side="left", padx=(0, 12))
        lbl(left_col, "CUSTOMER RECEIPT", size=9, bold=True, color=ACCENT).pack(pady=(0, 4))
        txt = tk.Text(left_col, font=("Courier New", 10), bg=BG3, fg=TEXT,
                      width=44, height=len(lines)+2, padx=10, pady=10,
                      relief="flat", state="normal")
        txt.insert("1.0", receipt_text)
        txt.config(state="disabled")
        txt.pack()
        btn(left_col, "Print / Save Customer", lambda: self._save(receipt_text, "receipt"),
            color=GREEN, size=9).pack(pady=(6, 0), fill="x")
        btn(left_col, "Send to Thermal Printer",
            lambda: self._thermal_print(self._order_data, receipt_type="customer"),
            color=ACCENT, size=9).pack(pady=(4, 0), fill="x")

        # Kitchen receipt column
        kitchen_lines = self._build_kitchen_lines(order, items, table)
        kitchen_text = "\n".join(kitchen_lines)

        right_col = tk.Frame(cols_frame, bg=BG2)
        right_col.pack(side="left")
        lbl(right_col, "KITCHEN RECEIPT", size=9, bold=True, color=YELLOW).pack(pady=(0, 4))
        ktxt = tk.Text(right_col, font=("Courier New", 10), bg=BG3, fg=TEXT,
                       width=32, height=len(kitchen_lines)+2, padx=10, pady=10,
                       relief="flat", state="normal")
        ktxt.insert("1.0", kitchen_text)
        ktxt.config(state="disabled")
        ktxt.pack()
        btn(right_col, "Print / Save Kitchen", lambda: self._save(kitchen_text, "kitchen"),
            color=YELLOW, fg=BG, size=9).pack(pady=(6, 0), fill="x")
        btn(right_col, "Send to Thermal Printer",
            lambda: self._thermal_print(self._order_data, receipt_type="kitchen"),
            color=ORANGE, fg=BG, size=9).pack(pady=(4, 0), fill="x")

        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+30}")

    def _build_kitchen_lines(self, order, items, table):
        cafe = database.get_setting("cafe_name", "CAFE POS")
        now = order.get("paid_at", order["created_at"])[:16]
        lines = [
            f"{'='*30}",
            f"{'KITCHEN ORDER':^30}",
            f"{cafe:^30}",
            f"{'='*30}",
            f"Order : {order['receipt_number']}",
            f"Time  : {now}",
            f"Table : {table}",
            f"Server: {order['cashier_name']}",
            f"{'─'*30}",
            f"{'ITEM':<20}{'QTY':>8}",
            f"{'─'*30}",
        ]
        for it in items:
            name = it["item_name"][:18]
            lines.append(f"{name:<20}{it['quantity']:>8}")
        lines += [
            f"{'='*30}",
            f"{'** SERVE IMMEDIATELY **':^30}",
            f"{'='*30}",
        ]
        return lines

    def _save(self, text, receipt_type="receipt"):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, f"{receipt_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(path, "w") as f:
            f.write(text)
        try:
            os.startfile(path)
        except Exception:
            pass
        messagebox.showinfo("Saved", f"Saved to:\n{path}", parent=self)

    def _thermal_print(self, data, receipt_type="customer"):
        conn_type = database.get_setting("printer_connection", "").strip()
        address   = database.get_setting("printer_address", "").strip()

        if not conn_type or not address:
            messagebox.showerror(
                "Printer Not Configured",
                "Please configure the thermal printer in Settings first.\n\n"
                "Connection type: network or usb\n"
                "Address: IP (e.g. 192.168.1.100) or USB printer name",
                parent=self
            )
            return

        order  = data["order"]
        items  = data["items"]
        cafe   = database.get_setting("cafe_name", "CAFE POS")
        currency  = database.get_setting("currency_symbol", "KSh")
        footer    = database.get_setting("receipt_footer", "")
        tax_rate  = database.get_setting("tax_rate", "16")
        address_t = database.get_setting("address", "")
        phone     = database.get_setting("phone", "")
        kra_pin   = database.get_setting("kra_pin", "")
        header    = database.get_setting("receipt_header", "")

        try:
            if receipt_type == "customer":
                raw = printer.build_customer_receipt(
                    order, items, cafe, currency, footer, tax_rate,
                    address=address_t, phone=phone, kra_pin=kra_pin, receipt_header=header
                )
            else:
                raw = printer.build_kitchen_receipt(order, items, cafe)

            printer.send_to_printer(raw, conn_type, address)
            messagebox.showinfo("Printed", "Receipt sent to thermal printer.", parent=self)
        except Exception as exc:
            messagebox.showerror("Print Error", str(exc), parent=self)


# ══════════════════════════════════════════════════════════════════════════════
# MENU MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
class MenuManagementScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)
        NavBar(self, app).pack(fill="x")
        sep(self).pack(fill="x")

        self.selected_item_id = None
        self.selected_cat_id = None

        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=8, pady=8)

        # Left tree
        left = tk.Frame(content, bg=BG2, width=300)
        left.pack(side="left", fill="y", padx=(0, 6))
        left.pack_propagate(False)

        lbl(left, "CATEGORIES & ITEMS", bold=True, color=ACCENT).pack(pady=8)

        toolbar = tk.Frame(left, bg=BG2)
        toolbar.pack(fill="x", padx=6)
        btn(toolbar, "+ Cat", self._add_category, color=BG3, size=9).pack(side="left", padx=2)
        btn(toolbar, "+ Item", self._add_item, color=GREEN, size=9).pack(side="left", padx=2)
        btn(toolbar, "Edit", self._edit_selected, color=YELLOW, size=9).pack(side="left", padx=2)
        btn(toolbar, "Delete", self._delete_selected, color=ACCENT, size=9).pack(side="left", padx=2)

        tree_frame = tk.Frame(left, bg=BG2)
        tree_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree = ttk.Treeview(tree_frame, style="S.Treeview", show="tree headings",
                                 columns=("Price", "Available"))
        self.tree.heading("#0", text="Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Available", text="Avail")
        self.tree.column("#0", width=150)
        self.tree.column("Price", width=70)
        self.tree.column("Available", width=50)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Right form
        right = tk.Frame(content, bg=BG2, padx=20, pady=16)
        right.pack(side="left", fill="both", expand=True)

        lbl(right, "ITEM DETAILS", bold=True, color=ACCENT).pack(pady=(0, 12), anchor="w")

        lbl(right, "Name", color=SUBTEXT, size=9).pack(anchor="w")
        self.name_var = tk.StringVar()
        ent(right, textvariable=self.name_var, width=30).pack(anchor="w", pady=(2, 8))

        lbl(right, "Category", color=SUBTEXT, size=9).pack(anchor="w")
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(right, textvariable=self.cat_var, width=28)
        self.cat_combo.pack(anchor="w", pady=(2, 8))

        lbl(right, "Price", color=SUBTEXT, size=9).pack(anchor="w")
        self.price_var = tk.StringVar()
        ent(right, textvariable=self.price_var, width=15).pack(anchor="w", pady=(2, 8))

        lbl(right, "Description", color=SUBTEXT, size=9).pack(anchor="w")
        self.desc_text = tk.Text(right, width=30, height=4, bg=BG3, fg=TEXT,
                                 font=(FONTSANS, 10), relief="flat", bd=3, insertbackground=ACCENT)
        self.desc_text.pack(anchor="w", pady=(2, 12))

        self.avail_var = tk.BooleanVar(value=True)
        tk.Checkbutton(right, text="Available", variable=self.avail_var,
                       bg=BG2, fg=TEXT, selectcolor=BG3,
                       font=(FONTSANS, 10)).pack(anchor="w", pady=4)

        row = tk.Frame(right, bg=BG2)
        row.pack(anchor="w", pady=8)
        btn(row, "Save", self._save_item, color=GREEN).pack(side="left", padx=4)
        btn(row, "Clear", self._clear_form, color=BG3).pack(side="left", padx=4)
        btn(row, "Toggle Availability", self._toggle_avail, color=YELLOW).pack(side="left", padx=4)

        self._refresh_tree()
        self._refresh_cat_combo()

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        currency = database.get_setting("currency_symbol", "KSh")
        for cat in database.get_categories():
            cat_node = self.tree.insert("", "end", iid=f"cat_{cat['id']}",
                                        text=cat["name"], open=True)
            for item in database.get_items_by_category(cat["id"]):
                self.tree.insert(cat_node, "end", iid=f"item_{item['id']}",
                                 text=item["name"],
                                 values=(f"{currency} {item['price']:,.0f}",
                                         "✓" if item["is_available"] else "✗"))

    def _refresh_cat_combo(self):
        cats = database.get_categories()
        self.cat_combo["values"] = [c["name"] for c in cats]
        self._cats = {c["name"]: c["id"] for c in cats}

    def _on_tree_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        if iid.startswith("item_"):
            item_id = int(iid.split("_")[1])
            self.selected_item_id = item_id
            all_items = database.get_all_items()
            item = next((i for i in all_items if i["id"] == item_id), None)
            if item:
                self.name_var.set(item["name"])
                self.cat_var.set(item["category_name"])
                self.price_var.set(str(item["price"]))
                self.desc_text.delete("1.0", "end")
                self.desc_text.insert("1.0", item.get("description", ""))
                self.avail_var.set(bool(item["is_available"]))

    def _save_item(self):
        name = self.name_var.get().strip()
        cat_name = self.cat_var.get()
        if not name:
            messagebox.showerror("Error", "Item name is required.")
            return
        cat_id = self._cats.get(cat_name)
        if not cat_id:
            messagebox.showerror("Error", "Select a valid category.")
            return
        try:
            price = float(self.price_var.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid price.")
            return
        desc = self.desc_text.get("1.0", "end").strip()

        if self.selected_item_id:
            database.update_menu_item(self.selected_item_id, cat_id, name, price, desc)
        else:
            database.create_menu_item(cat_id, name, price, desc)

        self._clear_form()
        self._refresh_tree()

    def _clear_form(self):
        self.selected_item_id = None
        self.name_var.set("")
        self.price_var.set("")
        self.desc_text.delete("1.0", "end")
        self.avail_var.set(True)

    def _add_category(self):
        name = simpledialog.askstring("New Category", "Category name:", parent=self)
        if name:
            try:
                database.create_category(name.strip())
                self._refresh_tree()
                self._refresh_cat_combo()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _add_item(self):
        self._clear_form()

    def _edit_selected(self):
        pass  # Selection already loads into form

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        if iid.startswith("item_"):
            item_id = int(iid.split("_")[1])
            if messagebox.askyesno("Delete", "Delete this menu item?"):
                database.delete_menu_item(item_id)
                self._clear_form()
                self._refresh_tree()
        elif iid.startswith("cat_"):
            cat_id = int(iid.split("_")[1])
            if messagebox.askyesno("Delete Category", "Delete this category and ALL its items?"):
                items = database.get_items_by_category(cat_id)
                for i in items:
                    database.delete_menu_item(i["id"])
                database.delete_category(cat_id)
                self._refresh_tree()
                self._refresh_cat_combo()

    def _toggle_avail(self):
        if self.selected_item_id:
            database.toggle_item_availability(self.selected_item_id)
            self._refresh_tree()


# ══════════════════════════════════════════════════════════════════════════════
# TABLE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
class TableManagementScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)
        NavBar(self, app).pack(fill="x")
        sep(self).pack(fill="x")

        lbl(self, "TABLE MANAGEMENT", size=12, bold=True, color=ACCENT).pack(pady=10)

        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", padx=16, pady=4)
        btn(toolbar, "+ Add Table", self._add_table, color=GREEN).pack(side="left", padx=4)
        btn(toolbar, "Delete", self._delete_table, color=ACCENT).pack(side="left", padx=4)
        btn(toolbar, "Set Free", lambda: self._set_status("free"), color=BG3).pack(side="left", padx=4)
        btn(toolbar, "Set Occupied", lambda: self._set_status("occupied"), color=YELLOW).pack(side="left", padx=4)
        btn(toolbar, "Set Reserved", lambda: self._set_status("reserved"), color=ORANGE).pack(side="left", padx=4)

        cols = ("Table", "Capacity", "Status")
        widths = (150, 100, 120)
        f = tk.Frame(self, bg=BG)
        f.pack(fill="both", expand=True, padx=16, pady=8)
        self.tree = ttk.Treeview(f, columns=cols, show="headings",
                                 height=18, style="S.Treeview")
        vsb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        lbl(self, "  Green=Free   Orange=Occupied   Red=Reserved",
            size=9, color=SUBTEXT).pack(anchor="w", padx=16, pady=4)

        self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for t in database.get_all_tables():
            tag = {"free": "green", "occupied": "orange", "reserved": "red"}.get(t["status"], "")
            self.tree.insert("", "end", iid=str(t["id"]),
                             values=(t["table_number"], t["capacity"], t["status"].upper()),
                             tags=(tag,))
        self.tree.tag_configure("green", foreground=GREEN)
        self.tree.tag_configure("orange", foreground=YELLOW)
        self.tree.tag_configure("red", foreground=ACCENT)

    def _add_table(self):
        num = simpledialog.askstring("Add Table", "Table number (e.g. T7):", parent=self)
        if num:
            cap = simpledialog.askinteger("Capacity", "Seating capacity:", parent=self, minvalue=1, maxvalue=50)
            if cap:
                try:
                    database.create_table(num.strip(), cap)
                    self._refresh()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def _delete_table(self):
        sel = self.tree.selection()
        if not sel:
            return
        if messagebox.askyesno("Delete", "Delete selected table?"):
            try:
                database.delete_table(int(sel[0]))
                self._refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _set_status(self, status):
        sel = self.tree.selection()
        if not sel:
            return
        database.update_table_status(int(sel[0]), status)
        self._refresh()


# ══════════════════════════════════════════════════════════════════════════════
# ORDER HISTORY
# ══════════════════════════════════════════════════════════════════════════════
class OrderHistoryScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)
        NavBar(self, app).pack(fill="x")
        sep(self).pack(fill="x")

        lbl(self, "ORDER HISTORY", size=12, bold=True, color=ACCENT).pack(pady=10)

        filt = tk.Frame(self, bg=BG)
        filt.pack(fill="x", padx=16, pady=4)
        lbl(filt, "From:", size=9, color=SUBTEXT).pack(side="left")
        self.from_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ent(filt, width=12, textvariable=self.from_var).pack(side="left", padx=4)
        lbl(filt, "To:", size=9, color=SUBTEXT).pack(side="left")
        self.to_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ent(filt, width=12, textvariable=self.to_var).pack(side="left", padx=4)
        btn(filt, "Search", self._load, color=ACCENT, size=9).pack(side="left", padx=6)
        btn(filt, "Export CSV", self._export, color=BG3, size=9).pack(side="right", padx=4)

        cols = ("Receipt#", "Date", "Table", "Cashier", "Items", "Total", "Payment", "Status")
        widths = (140, 140, 80, 120, 50, 90, 80, 70)
        f = tk.Frame(self, bg=BG)
        f.pack(fill="both", expand=True, padx=16, pady=4)
        self.tree = ttk.Treeview(f, columns=cols, show="headings",
                                 height=18, style="S.Treeview")
        vsb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self._view_receipt)

        self._orders = []
        self._load()

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        orders = database.get_orders_by_date_range(
            self.from_var.get(), self.to_var.get()
        )
        self._orders = orders
        currency = database.get_setting("currency_symbol", "KSh")
        for o in orders:
            data = database.get_order_with_items(o["id"])
            item_count = len(data["items"]) if data else 0
            self.tree.insert("", "end", iid=str(o["id"]),
                             values=(o["receipt_number"],
                                     o["created_at"][:16],
                                     o.get("table_number") or "Takeaway",
                                     o["cashier_name"],
                                     item_count,
                                     f"{currency} {o['total']:,.2f}",
                                     o["payment_method"].upper() if o["payment_method"] else "-",
                                     o["status"].upper()))

    def _view_receipt(self, _):
        sel = self.tree.selection()
        if sel:
            ReceiptWindow(self, int(sel[0]))

    def _export(self):
        if not self._orders:
            messagebox.showinfo("No Data", "No orders to export.")
            return
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Receipt#", "Date", "Table", "Cashier", "Subtotal",
                             "Discount", "Tax", "Total", "Payment", "Status"])
            for o in self._orders:
                writer.writerow([o["receipt_number"], o["created_at"],
                                  o.get("table_number") or "Takeaway",
                                  o["cashier_name"], o["subtotal"],
                                  o["discount_amount"], o["tax_amount"],
                                  o["total"], o["payment_method"], o["status"]])
        messagebox.showinfo("Exported", f"Saved to:\n{path}")


# ══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════════════════
class ReportsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)
        NavBar(self, app).pack(fill="x")
        sep(self).pack(fill="x")

        lbl(self, "SALES REPORTS", size=12, bold=True, color=ACCENT).pack(pady=10)

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=16)
        lbl(top, "Date:", size=9, color=SUBTEXT).pack(side="left")
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ent(top, width=14, textvariable=self.date_var).pack(side="left", padx=4)
        btn(top, "Load Report", self._load, color=ACCENT, size=9).pack(side="left", padx=6)

        nb = ttk.Notebook(self, style="TNotebook")
        nb.pack(fill="both", expand=True, padx=12, pady=8)

        # Summary tab
        self.summary_frame = tk.Frame(nb, bg=BG2)
        nb.add(self.summary_frame, text="Daily Summary")

        # Category tab
        self.cat_frame = tk.Frame(nb, bg=BG2)
        nb.add(self.cat_frame, text="By Category")

        # Top items tab
        self.items_frame = tk.Frame(nb, bg=BG2)
        nb.add(self.items_frame, text="Top Items")

        self._load()

    def _load(self):
        d = self.date_var.get()
        currency = database.get_setting("currency_symbol", "KSh")

        # Summary
        for w in self.summary_frame.winfo_children():
            w.destroy()
        data = database.get_daily_summary(d)
        s = data["summary"]
        orders = s["orders"] or 0
        revenue = s["revenue"] or 0
        avg = s["avg_order"] or 0

        info_frame = tk.Frame(self.summary_frame, bg=BG2)
        info_frame.pack(pady=20, padx=30)

        def stat(label_text, value, color=TEXT):
            row = tk.Frame(info_frame, bg=BG2)
            row.pack(fill="x", pady=4)
            lbl(row, label_text, size=11, color=SUBTEXT, bold=False).pack(side="left")
            lbl(row, str(value), size=13, bold=True, color=color).pack(side="right")

        stat("Total Orders:", orders, YELLOW)
        stat(f"Total Revenue ({currency}):", f"{revenue:,.2f}", GREEN)
        stat(f"Average Order ({currency}):", f"{avg:,.2f}")

        if data["by_method"]:
            sep(info_frame).pack(fill="x", pady=10)
            lbl(info_frame, "By Payment Method:", size=10, bold=True, color=ACCENT).pack(anchor="w", pady=4)
            for m in data["by_method"]:
                row = tk.Frame(info_frame, bg=BG2)
                row.pack(fill="x", pady=2)
                lbl(row, f"  {m['payment_method'].upper()}", size=10).pack(side="left")
                lbl(row, f"{m['cnt']} orders  |  {currency} {m['total']:,.2f}", size=10, color=YELLOW).pack(side="right")

        # Category
        for w in self.cat_frame.winfo_children():
            w.destroy()
        cat_data = database.get_sales_by_category(d)
        if cat_data:
            cols = ("Category", "Items Sold", f"Revenue ({currency})")
            f = tk.Frame(self.cat_frame, bg=BG2)
            f.pack(fill="both", expand=True, padx=16, pady=16)
            tree = ttk.Treeview(f, columns=cols, show="headings", height=12, style="S.Treeview")
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=180, anchor="w")
            for row in cat_data:
                tree.insert("", "end", values=(row["category"], row["qty"], f"{row['revenue']:,.2f}"))
            tree.pack(fill="both", expand=True)
        else:
            lbl(self.cat_frame, "No sales data for this date.", color=SUBTEXT, size=11).pack(pady=40)

        # Top Items
        for w in self.items_frame.winfo_children():
            w.destroy()
        item_data = database.get_top_items(d)
        if item_data:
            cols = ("Rank", "Item", "Qty Sold", f"Revenue ({currency})")
            f = tk.Frame(self.items_frame, bg=BG2)
            f.pack(fill="both", expand=True, padx=16, pady=16)
            tree = ttk.Treeview(f, columns=cols, show="headings", height=12, style="S.Treeview")
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="w")
            for i, row in enumerate(item_data, 1):
                tree.insert("", "end", values=(i, row["item_name"], row["qty"], f"{row['revenue']:,.2f}"))
            tree.pack(fill="both", expand=True)
        else:
            lbl(self.items_frame, "No sales data for this date.", color=SUBTEXT, size=11).pack(pady=40)


# ══════════════════════════════════════════════════════════════════════════════
# STAFF MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
class StaffManagementScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)
        NavBar(self, app).pack(fill="x")
        sep(self).pack(fill="x")

        try:
            auth.Session.require_admin()
        except auth.PermissionError:
            lbl(self, "Admin access required.", size=14, color=ACCENT).pack(pady=60)
            return

        lbl(self, "STAFF MANAGEMENT", size=12, bold=True, color=ACCENT).pack(pady=10)

        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", padx=16, pady=4)
        btn(toolbar, "+ Add Staff", self._add_staff, color=GREEN).pack(side="left", padx=4)
        btn(toolbar, "Edit", self._edit_staff, color=YELLOW).pack(side="left", padx=4)
        btn(toolbar, "Toggle Active", self._toggle_active, color=ORANGE).pack(side="left", padx=4)

        cols = ("Name", "Username", "Role", "Status")
        widths = (180, 130, 100, 90)
        f = tk.Frame(self, bg=BG)
        f.pack(fill="both", expand=True, padx=16, pady=8)
        self.tree = ttk.Treeview(f, columns=cols, show="headings",
                                 height=16, style="S.Treeview")
        vsb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for s in database.get_all_staff():
            status = "Active" if s["is_active"] else "Inactive"
            tag = "active" if s["is_active"] else "inactive"
            self.tree.insert("", "end", iid=str(s["id"]),
                             values=(s["full_name"], s["username"],
                                     s["role"].upper(), status), tags=(tag,))
        self.tree.tag_configure("active", foreground=GREEN)
        self.tree.tag_configure("inactive", foreground=ACCENT)

    def _add_staff(self):
        StaffDialog(self, None, self._refresh)

    def _edit_staff(self):
        sel = self.tree.selection()
        if not sel:
            return
        staff = database.get_all_staff()
        staff_dict = next((s for s in staff if str(s["id"]) == sel[0]), None)
        if staff_dict:
            StaffDialog(self, staff_dict, self._refresh)

    def _toggle_active(self):
        sel = self.tree.selection()
        if not sel:
            return
        database.toggle_staff_active(int(sel[0]))
        self._refresh()


class StaffDialog(tk.Toplevel):
    def __init__(self, parent, staff, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.staff = staff
        editing = staff is not None

        self.title("Edit Staff" if editing else "Add Staff")
        self.configure(bg=BG2)
        self.resizable(False, False)
        self.grab_set()

        frm = tk.Frame(self, bg=BG2, padx=24, pady=16)
        frm.pack()

        lbl(frm, "Full Name", color=SUBTEXT, size=9).pack(anchor="w")
        self.name_var = tk.StringVar(value=staff["full_name"] if editing else "")
        ent(frm, textvariable=self.name_var, width=28).pack(fill="x", pady=(2, 8))

        lbl(frm, "Username", color=SUBTEXT, size=9).pack(anchor="w")
        self.user_var = tk.StringVar(value=staff["username"] if editing else "")
        ent(frm, textvariable=self.user_var, width=28).pack(fill="x", pady=(2, 8))

        lbl(frm, "Password" + (" (leave blank to keep)" if editing else ""),
            color=SUBTEXT, size=9).pack(anchor="w")
        self.pass_var = tk.StringVar()
        ent(frm, textvariable=self.pass_var, width=28, show="●").pack(fill="x", pady=(2, 8))

        lbl(frm, "Role", color=SUBTEXT, size=9).pack(anchor="w")
        self.role_var = tk.StringVar(value=staff["role"] if editing else "cashier")
        ttk.Combobox(frm, textvariable=self.role_var,
                     values=["cashier", "admin"], width=26).pack(fill="x", pady=(2, 12))

        row = tk.Frame(frm, bg=BG2)
        row.pack()
        btn(row, "Save", self._save, color=GREEN).pack(side="left", padx=6, ipady=4)
        btn(row, "Cancel", self.destroy, color=ACCENT).pack(side="left", padx=6, ipady=4)

        self.geometry(f"+{parent.winfo_rootx()+120}+{parent.winfo_rooty()+80}")

    def _save(self):
        name = self.name_var.get().strip()
        username = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        role = self.role_var.get()

        if not name or not username:
            messagebox.showerror("Error", "Name and username are required.", parent=self)
            return
        if not self.staff and not password:
            messagebox.showerror("Error", "Password is required for new staff.", parent=self)
            return

        try:
            if self.staff:
                database.update_staff(self.staff["id"], name, role, password or None)
            else:
                database.create_staff(username, password, name, role)
            self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
class SettingsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)
        NavBar(self, app).pack(fill="x")
        sep(self).pack(fill="x")

        try:
            auth.Session.require_admin()
        except auth.PermissionError:
            lbl(self, "Admin access required.", size=14, color=ACCENT).pack(pady=60)
            return

        lbl(self, "SYSTEM SETTINGS", size=12, bold=True, color=ACCENT).pack(pady=10)

        frm = tk.Frame(self, bg=BG2, padx=32, pady=24)
        frm.pack(padx=80, fill="x")

        fields = [
            ("cafe_name", "Cafe Name"),
            ("tax_rate", "Tax Rate (%)"),
            ("currency_symbol", "Currency Symbol"),
            ("receipt_footer", "Receipt Footer Text"),
            ("printer_connection", "Printer Connection  (network  or  usb)"),
            ("printer_address",   "Printer Address  (IP e.g. 192.168.1.100  or  Windows printer name)"),
        ]
        self.vars = {}
        for key, label_text in fields:
            lbl(frm, label_text, color=SUBTEXT, size=9).pack(anchor="w", pady=(8, 0))
            var = tk.StringVar(value=database.get_setting(key))
            ent(frm, textvariable=var, width=40).pack(fill="x", pady=(2, 0))
            self.vars[key] = var

        btn(frm, "Save Settings", self._save, color=GREEN, size=11).pack(pady=20, ipady=6)
        self.status_lbl = lbl(frm, "", color=GREEN, size=9)
        self.status_lbl.pack()

    def _save(self):
        for key, var in self.vars.items():
            database.set_setting(key, var.get().strip())
        self.status_lbl.config(text="Settings saved successfully.")
