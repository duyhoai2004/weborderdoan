import sqlite3
from flask import g

DATABASE = 'food_ordering.db'

def get_db():
    """Lấy kết nối database"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Đóng kết nối database"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Khởi tạo database và dữ liệu mẫu"""
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
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Tạo bảng đánh giá
    db.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            order_id INTEGER,
            customer_name TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')
    
    # Kiểm tra xem đã có dữ liệu chưa
    count = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    
    if count == 0:
        # Thêm dữ liệu mẫu với URL ảnh từ Unsplash
        sample_products = [
            ('Pizza Hải Sản', 'Pizza với tôm, mực, thanh cua tươi ngon', 120000, 
             'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500', 'Pizza'),
            
            ('Pizza Pepperoni', 'Pizza với xúc xích Pepperoni cay nồng', 110000, 
             'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=500', 'Pizza'),
            
            ('Burger Bò Phô Mai', 'Burger với thịt bò Úc, phô mai cheddar', 75000, 
             'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500', 'Burger'),
            
            ('Burger Gà Giòn', 'Burger gà rán giòn với sốt mayonnaise', 65000, 
             'https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=500', 'Burger'),
            
            ('Gà Rán Giòn', 'Gà rán giòn với công thức đặc biệt', 85000, 
             'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500', 'Gà rán'),
            
            ('Gà Sốt Cay', 'Gà rán sốt cay Hàn Quốc', 95000, 
             'https://images.unsplash.com/photo-1562967914-608f82629710?w=500', 'Gà rán'),
            
            ('Phở Bò Tái', 'Phở bò tái truyền thống Việt Nam', 55000, 
             'https://images.unsplash.com/photo-1591814468924-caf88d1232e1?w=500', 'Món Việt'),
            
            ('Bún Chả Hà Nội', 'Bún chả với thịt nướng thơm ngon', 50000, 
             'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=500', 'Món Việt'),
            
            ('Sushi Cá Hồi', 'Sushi cá hồi tươi ngon theo phong cách Nhật', 95000, 
             'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500', 'Món Nhật'),
            
            ('Ramen Tonkotsu', 'Ramen với nước dùng xương heo đậm đà', 85000, 
             'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=500', 'Món Nhật'),
            
            ('Mì Ý Carbonara', 'Mì Ý với sốt kem và thịt xông khói', 75000, 
             'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=500', 'Món Ý'),
            
            ('Mì Ý Bolognese', 'Mì Ý với sốt thịt bò bằm', 70000, 
             'https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?w=500', 'Món Ý'),
            
            ('Coca Cola', 'Nước ngọt Coca Cola 330ml', 15000, 
             'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=500', 'Đồ uống'),
            
            ('Pepsi', 'Nước ngọt Pepsi 330ml', 15000, 
             'https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=500', 'Đồ uống'),
            
            ('Trà Sữa Trân Châu', 'Trà sữa trân châu đường đen', 25000, 
             'https://images.unsplash.com/photo-1525385133512-2f3bdd039054?w=500', 'Đồ uống'),
            
            ('Nước Cam Ép', 'Nước cam tươi ép 100%', 30000, 
             'https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=500', 'Đồ uống'),
        ]
        
        db.executemany('''
            INSERT INTO products (name, description, price, image_url, category)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_products)
        
        print("✅ Đã thêm dữ liệu mẫu")
    
    db.commit()
    print("✅ Database đã được khởi tạo")