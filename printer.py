# printer.py — ESC/POS thermal printer support for CN710-UE (80mm, ESC/POS)
# Supports: Network (TCP/IP port 9100) and USB (Windows raw print queue)

import socket
import struct

# ── ESC/POS command constants ─────────────────────────────────────────────────
ESC = b'\x1b'
GS  = b'\x1d'

INIT          = ESC + b'@'          # Initialize printer
ALIGN_LEFT    = ESC + b'a\x00'
ALIGN_CENTER  = ESC + b'a\x01'
ALIGN_RIGHT   = ESC + b'a\x02'
BOLD_ON       = ESC + b'E\x01'
BOLD_OFF      = ESC + b'E\x00'
DOUBLE_HEIGHT = ESC + b'!\x10'
NORMAL_SIZE   = ESC + b'!\x00'
LINE_FEED     = b'\n'
CUT           = GS  + b'V\x41\x03'  # Partial cut with 3mm feed

PAPER_WIDTH   = 42   # characters at normal font on 80mm paper


def _encode(text):
    """Encode text to bytes, replacing unsupported chars."""
    return text.encode('ascii', errors='replace')


def build_customer_receipt(order, items, cafe, currency, footer, tax_rate, address="", phone="", receipt_header="", till_number=""):
    """Build ESC/POS byte sequence for a customer receipt."""
    buf = bytearray()
    buf += INIT

    def center_line(text, width=PAPER_WIDTH):
        return _encode(text.center(width)) + LINE_FEED

    def left_line(text):
        return _encode(text) + LINE_FEED

    def rule(char="=", width=PAPER_WIDTH):
        return _encode(char * width) + LINE_FEED

    # Header
    buf += ALIGN_CENTER
    buf += BOLD_ON + DOUBLE_HEIGHT
    buf += _encode(cafe[:PAPER_WIDTH].center(PAPER_WIDTH)) + LINE_FEED
    buf += NORMAL_SIZE + BOLD_OFF

    if address:
        buf += _encode(address[:PAPER_WIDTH].center(PAPER_WIDTH)) + LINE_FEED
    if phone:
        buf += _encode(phone[:PAPER_WIDTH].center(PAPER_WIDTH)) + LINE_FEED
    if receipt_header:
        buf += _encode(receipt_header[:PAPER_WIDTH].center(PAPER_WIDTH)) + LINE_FEED

    buf += rule("=")
    buf += ALIGN_LEFT

    # Order info
    buf += left_line(f"Receipt : {order['receipt_number']}")
    buf += left_line(f"Date    : {order.get('paid_at', order['created_at'])[:16]}")
    buf += left_line(f"Cashier : {order['cashier_name']}")
    table = order.get("table_number") or "Takeaway"
    buf += left_line(f"Table   : {table}")
    buf += rule("-")

    # Column header
    header = f"{'Item':<22}{'Qty':>4}{'Price':>8}{'Total':>8}"
    buf += BOLD_ON
    buf += left_line(header)
    buf += BOLD_OFF
    buf += rule("-")

    # Items
    for it in items:
        name = it["item_name"][:20]
        line = f"{name:<22}{it['quantity']:>4}{it['unit_price']:>8.0f}{it['line_total']:>8.0f}"
        buf += left_line(line)
        # Modifiers/notes if present
        if it.get("notes"):
            buf += left_line(f"  > {it['notes'][:38]}")

    buf += rule("-")

    # Totals
    buf += left_line(f"{'Subtotal':<30}{order['subtotal']:>12,.2f}")
    if order.get("discount_amount", 0):
        buf += left_line(f"{'Discount':<30}-{order['discount_amount']:>11,.2f}")
    buf += left_line(f"{'Tax (' + str(tax_rate) + '%)':<30}{order['tax_amount']:>12,.2f}")
    buf += rule("-")
    buf += BOLD_ON
    buf += left_line(f"{'TOTAL ' + currency:<30}{order['total']:>12,.2f}")
    buf += BOLD_OFF
    buf += rule("-")

    # Payment
    method = order.get("payment_method", "").upper()
    buf += left_line(f"Payment : {method}")
    if order.get("payment_reference"):
        buf += left_line(f"Ref     : {order['payment_reference']}")
    if order.get("payment_method") == "cash":
        buf += left_line(f"Tendered: {currency} {order.get('amount_tendered', 0):,.2f}")
        buf += left_line(f"Change  : {currency} {order.get('change_given', 0):,.2f}")

    # Footer
    buf += rule("=")
    buf += ALIGN_CENTER
    if footer:
        buf += _encode(footer[:PAPER_WIDTH].center(PAPER_WIDTH)) + LINE_FEED
    if till_number:
        buf += _encode(f"TILL NO: {till_number}".center(PAPER_WIDTH)) + LINE_FEED
    buf += rule("=")

    # Feed and cut
    buf += LINE_FEED * 3
    buf += CUT

    return bytes(buf)


def build_kitchen_receipt(order, items, cafe):
    """Build ESC/POS byte sequence for a kitchen order ticket."""
    buf = bytearray()
    buf += INIT
    buf += ALIGN_CENTER
    buf += BOLD_ON + DOUBLE_HEIGHT
    buf += _encode("KITCHEN ORDER".center(PAPER_WIDTH)) + LINE_FEED
    buf += NORMAL_SIZE + BOLD_OFF
    buf += _encode(cafe[:PAPER_WIDTH].center(PAPER_WIDTH)) + LINE_FEED

    def rule(char="=", width=PAPER_WIDTH):
        return _encode(char * width) + LINE_FEED

    buf += rule("=")
    buf += ALIGN_LEFT

    table = order.get("table_number") or "Takeaway"
    buf += _encode(f"Order : {order['receipt_number']}") + LINE_FEED
    buf += _encode(f"Time  : {order.get('paid_at', order['created_at'])[:16]}") + LINE_FEED
    buf += _encode(f"Table : {table}") + LINE_FEED
    buf += _encode(f"Server: {order['cashier_name']}") + LINE_FEED
    buf += rule("-")
    buf += BOLD_ON
    buf += _encode(f"{'ITEM':<30}{'QTY':>12}") + LINE_FEED
    buf += BOLD_OFF
    buf += rule("-")

    for it in items:
        name = it["item_name"][:28]
        buf += _encode(f"{name:<30}{it['quantity']:>12}") + LINE_FEED
        if it.get("notes"):
            buf += _encode(f"  > {it['notes'][:38]}") + LINE_FEED

    buf += rule("=")
    buf += ALIGN_CENTER
    buf += BOLD_ON
    buf += _encode("** SERVE IMMEDIATELY **".center(PAPER_WIDTH)) + LINE_FEED
    buf += BOLD_OFF
    buf += rule("=")
    buf += LINE_FEED * 3
    buf += CUT

    return bytes(buf)


# ── Transport layer ───────────────────────────────────────────────────────────

def print_network(data: bytes, ip: str, port: int = 9100, timeout: int = 5) -> None:
    """Send raw ESC/POS bytes to printer over TCP (Ethernet)."""
    with socket.create_connection((ip, port), timeout=timeout) as sock:
        sock.sendall(data)


def print_usb_windows(data: bytes, printer_name: str) -> None:
    """Send raw ESC/POS bytes to a Windows USB printer by name."""
    try:
        import win32print
    except ImportError:
        raise RuntimeError(
            "pywin32 is not installed.\n"
            "Run: pip install pywin32\n"
            "Then re-launch the application."
        )

    handle = win32print.OpenPrinter(printer_name)
    try:
        win32print.StartDocPrinter(handle, 1, ("ESC/POS Receipt", None, "RAW"))
        try:
            win32print.StartPagePrinter(handle)
            win32print.WritePrinter(handle, data)
            win32print.EndPagePrinter(handle)
        finally:
            win32print.EndDocPrinter(handle)
    finally:
        win32print.ClosePrinter(handle)


def send_to_printer(data: bytes, connection_type: str, address: str) -> None:
    """
    Route print job to the correct transport.

    connection_type: "network" or "usb"
    address:
        "network" → "192.168.1.100" or "192.168.1.100:9100"
        "usb"     → Windows printer name, e.g. "CN710-UE"
    """
    if connection_type == "network":
        parts = address.rsplit(":", 1)
        ip   = parts[0].strip()
        port = int(parts[1]) if len(parts) == 2 else 9100
        print_network(data, ip, port)
    elif connection_type == "usb":
        print_usb_windows(data, address.strip())
    else:
        raise ValueError(f"Unknown connection type: {connection_type!r}")


def list_windows_printers():
    """Return a list of installed printer names on Windows."""
    try:
        import win32print
        return [p[2] for p in win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )]
    except ImportError:
        return []
