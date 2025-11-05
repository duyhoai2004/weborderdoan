from database import get_db

class Product:
    @staticmethod
    def get_all():
        db = get_db()
        return db.execute('SELECT * FROM products WHERE is_available = 1').fetchall()
    
    @staticmethod
    def get_by_id(product_id):
        db = get_db()
        return db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    @staticmethod
    def create(name, description, price, image_url, category):
        db = get_db()
        db.execute(
            'INSERT INTO products (name, description, price, image_url, category) VALUES (?, ?, ?, ?, ?)',
            (name, description, price, image_url, category)
        )
        db.commit()
    
    @staticmethod
    def update(product_id, name, description, price, image_url, category):
        db = get_db()
        db.execute(
            'UPDATE products SET name=?, description=?, price=?, image_url=?, category=? WHERE id=?',
            (name, description, price, image_url, category, product_id)
        )
        db.commit()
    
    @staticmethod
    def delete(product_id):
        db = get_db()
        db.execute('UPDATE products SET is_available=0 WHERE id=?', (product_id,))
        db.commit()

class Order:
    @staticmethod
    def create(customer_name, customer_phone, customer_address, cart_items):
        db = get_db()
        
        # Tính tổng tiền
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        
        # Tạo đơn hàng
        cursor = db.execute(
            'INSERT INTO orders (customer_name, customer_phone, customer_address, total_amount) VALUES (?, ?, ?, ?)',
            (customer_name, customer_phone, customer_address, total_amount)
        )
        order_id = cursor.lastrowid
        
        # Thêm chi tiết đơn hàng
        for item in cart_items:
            db.execute(
                'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                (order_id, item['id'], item['quantity'], item['price'])
            )
        
        db.commit()
        return order_id
    
    @staticmethod
    def get_all():
        db = get_db()
        return db.execute('''
            SELECT o.*, COUNT(oi.id) as item_count 
            FROM orders o 
            LEFT JOIN order_items oi ON o.id = oi.order_id 
            GROUP BY o.id 
            ORDER BY o.created_at DESC
        ''').fetchall()
    
    @staticmethod
    def get_by_id(order_id):
        db = get_db()
        order = db.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
        if order:
            items = db.execute('''
                SELECT oi.*, p.name, p.image_url 
                FROM order_items oi 
                JOIN products p ON oi.product_id = p.id 
                WHERE oi.order_id = ?
            ''', (order_id,)).fetchall()
            return order, items
        return None, []
    
    @staticmethod
    def update_status(order_id, status):
        db = get_db()
        db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        db.commit()