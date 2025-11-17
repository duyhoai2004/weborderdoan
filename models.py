from database import get_db

class Product:
    """Model cho sản phẩm"""
    
    @staticmethod
    def get_all():
        """Lấy tất cả sản phẩm còn bán"""
        db = get_db()
        return db.execute(
            'SELECT * FROM products WHERE is_available = 1 ORDER BY created_at DESC'
        ).fetchall()
    
    @staticmethod
    def get_by_id(product_id):
        """Lấy sản phẩm theo ID"""
        db = get_db()
        return db.execute(
            'SELECT * FROM products WHERE id = ?', 
            (product_id,)
        ).fetchone()
    
    @staticmethod
    def get_by_category(category):
        """Lấy sản phẩm theo danh mục"""
        db = get_db()
        return db.execute(
            'SELECT * FROM products WHERE category = ? AND is_available = 1',
            (category,)
        ).fetchall()
    
    @staticmethod
    def get_categories():
        """Lấy danh sách các danh mục"""
        db = get_db()
        result = db.execute(
            'SELECT DISTINCT category FROM products WHERE is_available = 1'
        ).fetchall()
        return [row['category'] for row in result]
    
    @staticmethod
    def create(name, description, price, image_url, category):
        """Tạo sản phẩm mới"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO products (name, description, price, image_url, category) 
               VALUES (?, ?, ?, ?, ?)''',
            (name, description, price, image_url, category)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update(product_id, name, description, price, image_url, category):
        """Cập nhật sản phẩm"""
        db = get_db()
        db.execute(
            '''UPDATE products 
               SET name=?, description=?, price=?, image_url=?, category=? 
               WHERE id=?''',
            (name, description, price, image_url, category, product_id)
        )
        db.commit()
    
    @staticmethod
    def delete(product_id):
        """Xóa sản phẩm (soft delete)"""
        db = get_db()
        db.execute(
            'UPDATE products SET is_available=0 WHERE id=?',
            (product_id,)
        )
        db.commit()
    
    @staticmethod
    def search(keyword):
        """Tìm kiếm sản phẩm"""
        db = get_db()
        keyword = f'%{keyword}%'
        return db.execute(
            '''SELECT * FROM products 
               WHERE (name LIKE ? OR description LIKE ?) AND is_available = 1''',
            (keyword, keyword)
        ).fetchall()


class Order:
    """Model cho đơn hàng"""
    
    @staticmethod
    def create(customer_name, customer_phone, customer_address, cart_items):
        """Tạo đơn hàng mới"""
        db = get_db()
        
        # Tính tổng tiền
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        
        # Tạo đơn hàng
        cursor = db.execute(
            '''INSERT INTO orders (customer_name, customer_phone, customer_address, total_amount) 
               VALUES (?, ?, ?, ?)''',
            (customer_name, customer_phone, customer_address, total_amount)
        )
        order_id = cursor.lastrowid
        
        # Thêm chi tiết đơn hàng
        for item in cart_items:
            db.execute(
                '''INSERT INTO order_items (order_id, product_id, quantity, price) 
                   VALUES (?, ?, ?, ?)''',
                (order_id, item['id'], item['quantity'], item['price'])
            )
        
        db.commit()
        return order_id
    
    @staticmethod
    def get_all():
        """Lấy tất cả đơn hàng"""
        db = get_db()
        return db.execute(
            '''SELECT o.*, COUNT(oi.id) as item_count 
               FROM orders o 
               LEFT JOIN order_items oi ON o.id = oi.order_id 
               GROUP BY o.id 
               ORDER BY o.created_at DESC'''
        ).fetchall()
    
    @staticmethod
    def get_by_id(order_id):
        """Lấy đơn hàng theo ID"""
        db = get_db()
        order = db.execute(
            'SELECT * FROM orders WHERE id = ?', 
            (order_id,)
        ).fetchone()
        
        if order:
            items = db.execute(
                '''SELECT oi.*, p.name, p.image_url 
                   FROM order_items oi 
                   JOIN products p ON oi.product_id = p.id 
                   WHERE oi.order_id = ?''',
                (order_id,)
            ).fetchall()
            return order, items
        
        return None, []
    
    @staticmethod
    def update_status(order_id, status):
        """Cập nhật trạng thái đơn hàng"""
        db = get_db()
        db.execute(
            'UPDATE orders SET status = ? WHERE id = ?',
            (status, order_id)
        )
        db.commit()
    
    @staticmethod
    def get_by_status(status):
        """Lấy đơn hàng theo trạng thái"""
        db = get_db()
        return db.execute(
            'SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC',
            (status,)
        ).fetchall()
    
    @staticmethod
    def get_statistics():
        """Lấy thống kê đơn hàng"""
        db = get_db()
        stats = {
            'total': 0,
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'cancelled': 0,
            'revenue': 0
        }
        
        # Tổng đơn hàng
        result = db.execute('SELECT COUNT(*) as count FROM orders').fetchone()
        stats['total'] = result['count']
        
        # Đơn hàng theo trạng thái
        for status in ['pending', 'processing', 'completed', 'cancelled']:
            result = db.execute(
                'SELECT COUNT(*) as count FROM orders WHERE status = ?',
                (status,)
            ).fetchone()
            stats[status] = result['count']
        
        # Doanh thu (chỉ tính đơn hoàn thành)
        result = db.execute(
            'SELECT SUM(total_amount) as revenue FROM orders WHERE status = "completed"'
        ).fetchone()
        stats['revenue'] = result['revenue'] or 0
        
        return stats
    
    @staticmethod
    def get_orders_today():
        """Lấy số đơn hàng hôm nay"""
        db = get_db()
        result = db.execute(
            """SELECT COUNT(*) as count FROM orders 
               WHERE DATE(created_at) = DATE('now', 'localtime')"""
        ).fetchone()
        return result['count'] if result else 0
    
    @staticmethod
    def get_orders_this_week():
        """Lấy số đơn hàng tuần này"""
        db = get_db()
        result = db.execute(
            """SELECT COUNT(*) as count FROM orders 
               WHERE DATE(created_at) >= DATE('now', 'localtime', '-7 days')"""
        ).fetchone()
        return result['count'] if result else 0
    
    @staticmethod
    def get_orders_this_month():
        """Lấy số đơn hàng tháng này"""
        db = get_db()
        result = db.execute(
            """SELECT COUNT(*) as count FROM orders 
               WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')"""
        ).fetchone()
        return result['count'] if result else 0
    
    @staticmethod
    def get_revenue_by_date(days=7):
        """Lấy doanh thu theo ngày (dùng cho line chart)"""
        db = get_db()
        
        # Tạo danh sách các ngày
        from datetime import datetime, timedelta
        dates = []
        revenues = {}
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            dates.append(date)
            revenues[date] = 0
        
        # Lấy dữ liệu thực từ database
        result = db.execute(
            """SELECT DATE(created_at) as date, SUM(total_amount) as revenue
               FROM orders 
               WHERE status = 'completed' 
               AND DATE(created_at) >= DATE('now', 'localtime', '-' || ? || ' days')
               GROUP BY DATE(created_at)
               ORDER BY date ASC""",
            (days,)
        ).fetchall()
        
        # Gán dữ liệu vào dict
        for row in result:
            if row['date'] in revenues:
                revenues[row['date']] = float(row['revenue'])
        
        # Trả về list có đầy đủ các ngày
        return [{'date': date, 'revenue': revenues[date]} for date in dates]
    
    @staticmethod
    def get_orders_by_status():
        """Lấy số lượng đơn hàng theo trạng thái (dùng cho pie chart)"""
        db = get_db()
        result = db.execute(
            """SELECT status, COUNT(*) as count 
               FROM orders 
               GROUP BY status
               HAVING count > 0"""
        ).fetchall()
        
        # Nếu không có dữ liệu, trả về mẫu
        if not result:
            return [
                {'status': 'pending', 'count': 0},
                {'status': 'completed', 'count': 0}
            ]
        
        return result
    
    @staticmethod
    def get_top_products(limit=10):
        """Lấy top sản phẩm bán chạy (dùng cho bar chart)"""
        db = get_db()
        result = db.execute(
            """SELECT p.name, SUM(oi.quantity) as total_sold, SUM(oi.quantity * oi.price) as revenue
               FROM order_items oi
               JOIN products p ON oi.product_id = p.id
               JOIN orders o ON oi.order_id = o.id
               WHERE o.status = 'completed'
               GROUP BY oi.product_id, p.name
               ORDER BY total_sold DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
        
        # Nếu không có dữ liệu, trả về danh sách rỗng
        if not result:
            return []
        
        return result
    
    @staticmethod
    def get_revenue_by_month(months=6):
        """Lấy doanh thu theo tháng"""
        db = get_db()
        result = db.execute(
            """SELECT strftime('%Y-%m', created_at) as month, SUM(total_amount) as revenue
               FROM orders 
               WHERE status = 'completed'
               AND DATE(created_at) >= DATE('now', '-' || ? || ' months')
               GROUP BY strftime('%Y-%m', created_at)
               ORDER BY month ASC""",
            (months,)
        ).fetchall()
        return result


class Review:
    """Model cho đánh giá sản phẩm"""
    
    @staticmethod
    def create(product_id, customer_name, rating, comment, order_id=None):
        """Tạo đánh giá mới"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO reviews (product_id, order_id, customer_name, rating, comment) 
               VALUES (?, ?, ?, ?, ?)''',
            (product_id, order_id, customer_name, rating, comment)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_product(product_id):
        """Lấy tất cả đánh giá của sản phẩm"""
        db = get_db()
        return db.execute(
            '''SELECT * FROM reviews 
               WHERE product_id = ? 
               ORDER BY created_at DESC''',
            (product_id,)
        ).fetchall()
    
    @staticmethod
    def get_all():
        """Lấy tất cả đánh giá"""
        db = get_db()
        return db.execute(
            '''SELECT r.*, p.name as product_name, p.image_url as product_image
               FROM reviews r
               JOIN products p ON r.product_id = p.id
               ORDER BY r.created_at DESC'''
        ).fetchall()
    
    @staticmethod
    def get_recent(limit=10):
        """Lấy đánh giá gần đây"""
        db = get_db()
        return db.execute(
            '''SELECT r.*, p.name as product_name, p.image_url as product_image
               FROM reviews r
               JOIN products p ON r.product_id = p.id
               ORDER BY r.created_at DESC
               LIMIT ?''',
            (limit,)
        ).fetchall()
    
    @staticmethod
    def get_average_rating(product_id):
        """Lấy điểm đánh giá trung bình của sản phẩm"""
        db = get_db()
        result = db.execute(
            '''SELECT AVG(rating) as avg_rating, COUNT(*) as review_count
               FROM reviews 
               WHERE product_id = ?''',
            (product_id,)
        ).fetchone()
        
        return {
            'average': round(result['avg_rating'], 1) if result['avg_rating'] else 0,
            'count': result['review_count']
        }
    
    @staticmethod
    def delete(review_id):
        """Xóa đánh giá"""
        db = get_db()
        db.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
        db.commit()
    
    @staticmethod
    def get_statistics():
        """Thống kê đánh giá"""
        db = get_db()
        
        # Tổng số đánh giá
        total = db.execute('SELECT COUNT(*) as count FROM reviews').fetchone()['count']
        
        # Đánh giá theo rating
        rating_dist = {}
        for rating in range(1, 6):
            count = db.execute(
                'SELECT COUNT(*) as count FROM reviews WHERE rating = ?',
                (rating,)
            ).fetchone()['count']
            rating_dist[rating] = count
        
        # Điểm trung bình
        avg = db.execute('SELECT AVG(rating) as avg FROM reviews').fetchone()['avg']
        
        return {
            'total': total,
            'average': round(avg, 1) if avg else 0,
            'distribution': rating_dist
        }