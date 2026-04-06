"""
Clears existing categories & menu items, then loads the real Queens Cafe menu.
Run once: python load_menu.py
"""
import sqlite3

conn = sqlite3.connect('cafe_pos.db')
cur = conn.cursor()

# ── Wipe existing data ────────────────────────────────────────────────────────
cur.execute('DELETE FROM order_item_modifiers')
cur.execute('DELETE FROM order_items')
cur.execute('DELETE FROM orders')
cur.execute('DELETE FROM menu_items')
cur.execute('DELETE FROM categories')
cur.execute('DELETE FROM sqlite_sequence WHERE name IN ("menu_items","categories")')

# ── Categories ────────────────────────────────────────────────────────────────
categories = [
    (1, 'Chicken'),
    (2, 'Beef'),
    (3, 'Fish'),
    (4, 'Ugali Meals'),
    (5, 'Other Meals'),
    (6, 'Rice'),
    (7, 'Snacks'),
    (8, 'Breakfast & Sides'),
    (9, 'Bread & Pastry'),
    (10, 'Hot Beverages'),
    (11, 'Cold Beverages'),
]
cur.executemany('INSERT INTO categories (id, name) VALUES (?,?)', categories)

# ── Menu items (category_id, name, price) ────────────────────────────────────
items = [
    # Chicken
    (1, '1/2 Chicken Stew Wet Fry Plain', 400),
    (1, '1/4 Chicken Chapati', 400),
    (1, '1/4 Chicken Chips', 450),
    (1, '1/4 Chicken Fry Ugali', 400),
    (1, '1/4 Chicken Wet Fry Ugali', 450),
    (1, 'Full Chicken', 1400),

    # Beef
    (2, 'Beef Fry / Stew Chips', 350),
    (2, 'Beef Fry / Stew Rice', 350),
    (2, 'Beef Fry Mokimo', 350),
    (2, 'Beef Fry Chapati', 300),
    (2, 'Beef Fry / Stew Ugali Brown', 300),
    (2, 'Beef Stew Plain', 250),
    (2, 'Beef Stew Ugali', 300),

    # Fish
    (3, 'Fish Fry Plain', 350),
    (3, 'Fish Fry Ugali', 400),
    (3, 'Fish Fry Chips', 400),
    (3, 'Fish Wet Fry Chips', 450),
    (3, 'Fish Fry Mokimo', 450),
    (3, 'Fish Wet Fry Makimo', 450),
    (3, 'Fish Wet Fry Ugali Brown', 450),

    # Ugali Meals
    (4, 'Ugali Mboga', 100),
    (4, 'Ugali Maziwa', 100),
    (4, 'Ugali Mboga Mix', 150),
    (4, 'Ugali Managu', 150),
    (4, 'Ugali Mixed Managu', 200),
    (4, 'Ugali Stew Beef', 300),
    (4, 'Ugali Plain White', 50),
    (4, 'Ugali Brown', 80),
    (4, 'Ugali Brown Mboga Mix', 150),
    (4, 'Ugali Brown Kienyeji', 230),
    (4, 'Ugali Saaga Mix', 150),
    (4, 'Ugali Skuma Mixed', 150),
    (4, 'Maharagwe Ugali', 110),

    # Other Meals
    (5, 'Pilau Plain', 150),
    (5, 'Pilau Special', 250),
    (5, 'Pilau Minji', 200),
    (5, 'Maharage Chapo', 100),
    (5, 'Minji Chapo', 100),
    (5, 'Soup Chapo', 90),
    (5, 'Chips Plain', 150),
    (5, 'Chips Half', 100),
    (5, 'Sausage Special', 150),
    (5, 'Kebab Special', 150),
    (5, 'Samosa Special', 150),
    (5, 'Chips Masala', 200),
    (5, 'Managu Plain', 100),
    (5, 'Cabbage Plain', 50),
    (5, 'Soup Plain', 50),
    (5, 'Beans Plain', 50),
    (5, 'Peas / Minji Plain', 60),
    (5, 'Ndengu Plain', 60),
    (5, 'Mix Managu Plain', 150),
    (5, 'Mboga Mix Plain', 100),
    (5, 'Matumbo Plain', 150),
    (5, 'Mix Maharage Plain', 150),
    (5, 'Mix Mbogo Plain', 100),
    (5, 'Gittheri Plain', 100),
    (5, 'Gittheri Special', 150),
    (5, 'Matoke Plain', 100),
    (5, 'Matoke Special', 150),

    # Rice
    (6, 'Rice Plain', 100),
    (6, 'Rice Special', 200),
    (6, 'Rice Maharage', 150),
    (6, 'Rice Minji', 150),
    (6, 'Rice Pilau Mixed', 150),
    (6, 'Rice Ndengu', 150),
    (6, 'Ndengu Chapo', 100),

    # Snacks
    (7, 'Ndazi', 30),
    (7, 'Chapati', 40),
    (7, 'Samosa', 50),
    (7, 'Sausage', 50),
    (7, 'Kebab', 50),
    (7, 'Fried Egg (2)', 60),

    # Breakfast & Sides
    (8, 'Chapati Brown', 50),
    (8, 'Egg Special (2 Eggs)', 100),
    (8, 'Scrambled Egg (2 Eggs)', 60),
    (8, 'Spanish Omelette (2 Eggs)', 100),
    (8, 'Special Spanish Omelette (2 Eggs)', 150),
    (8, 'Ngwace', 50),
    (8, 'Nduma', 50),

    # Bread & Pastry
    (9, 'Bread (3 Slices)', 40),
    (9, 'Cake Slice', 60),
    (9, 'Doughnut', 40),

    # Hot Beverages
    (10, 'White Tea', 40),
    (10, 'Tea Masala', 50),
    (10, 'Mixed Tea', 40),
    (10, 'Lemon Tea', 40),
    (10, 'Black Tea', 30),
    (10, 'White Coffee', 60),
    (10, 'Black Coffee', 60),
    (10, 'White Chocolate', 60),
    (10, 'Black Chocolate', 40),
    (10, 'White Milo', 50),
    (10, 'Black Milo', 40),
    (10, 'Cold/Hot Milk Glass', 50),
    (10, 'Mursik Glass', 70),

    # Cold Beverages
    (11, 'Fresh Juice', 60),
    (11, 'Cocktail Juice', 70),
    (11, 'Dawa', 100),
    (11, 'Soda 200ml', 30),
    (11, 'Soda 300ml', 50),
    (11, 'Soda 500ml', 80),
    (11, 'Soda Plastic 350ml', 60),
    (11, 'Mineral Water 500ml', 50),
    (11, 'Mineral Water 1L', 100),
    (11, 'Energy Drink', 70),
    (11, 'Fresh Milk 500ml', 70),
]

cur.executemany(
    'INSERT INTO menu_items (category_id, name, price) VALUES (?,?,?)',
    items
)

conn.commit()
conn.close()

print(f"Done! Loaded {len(items)} menu items across {len(categories)} categories.")
