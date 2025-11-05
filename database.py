import sqlite3
from flask import g
import os

DATABASE = 'food_ordering.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

 # Tạo bảng sản phẩm
    db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            category TEXT,
            is_available BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tạo bảng đơn hàng
    db.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tạo bảng chi tiết đơn hàng
    db.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Thêm dữ liệu mẫu
    sample_products = [
        ('Pizza Hải Sản', 'Pizza với tôm, mực, thanh cua', 120000, '/static/images/pizza.jpg', 'Pizza'),
        ('Burger Bò', 'Burger với thịt bò nướng, rau sống', 65000, '/static/images/burger.jpg', 'Burger'),
        ('Coca Cola', 'Nước ngọt Coca Cola', 15000, '/static/images/coca.jpg', 'Đồ uống'),
        ('Gà Rán', 'Gà rán giòn với sốt đặc biệt', 85000, '/static/images/chicken.jpg', 'Gà rán')
    ]
    
    db.executemany('''
        INSERT OR IGNORE INTO products (name, description, price, image_url, category)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_products)
    
    db.commit()