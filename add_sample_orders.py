"""
Script thêm đơn hàng mẫu để test thống kê
Chạy: python add_sample_orders.py
"""

from app import app
from models import Product, Order
from database import get_db
import random
from datetime import datetime, timedelta

def add_sample_orders():
    """Thêm đơn hàng mẫu"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("📦 THÊM DỮ LIỆU MẪU ĐỂ TEST THỐNG KÊ")
        print("="*60 + "\n")
        
        # Lấy danh sách sản phẩm
        products = Product.get_all()
        
        if not products:
            print("❌ Không có sản phẩm nào trong database!")
            print("Vui lòng chạy: python run.py trước")
            return
        
        print(f"✅ Tìm thấy {len(products)} sản phẩm\n")
        
        # Danh sách khách hàng mẫu
        customers = [
            ("Nguyễn Văn A", "0901234567", "123 Nguyễn Huệ, Q1, TP.HCM"),
            ("Trần Thị B", "0912345678", "456 Lê Lợi, Q1, TP.HCM"),
            ("Lê Văn C", "0923456789", "789 Hai Bà Trưng, Q3, TP.HCM"),
            ("Phạm Thị D", "0934567890", "321 Điện Biên Phủ, Q3, TP.HCM"),
            ("Hoàng Văn E", "0945678901", "654 Võ Văn Tần, Q3, TP.HCM"),
        ]
        
        # Trạng thái đơn hàng
        statuses = ['completed', 'completed', 'completed', 'processing', 'pending']
        
        db = get_db()
        orders_created = 0
        
        # Tạo đơn hàng trong 30 ngày qua
        for day in range(30):
            # Random số đơn hàng mỗi ngày (0-3 đơn)
            num_orders = random.randint(0, 3)
            
            for _ in range(num_orders):
                # Random khách hàng
                customer = random.choice(customers)
                
                # Random 1-4 sản phẩm
                num_products = random.randint(1, 4)
                selected_products = random.sample(list(products), num_products)
                
                # Tính tổng tiền
                total_amount = 0
                cart_items = []
                
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    total_amount += product['price'] * quantity
                    
                    cart_items.append({
                        'id': product['id'],
                        'price': product['price'],
                        'quantity': quantity
                    })
                
                # Random trạng thái
                status = random.choice(statuses)
                
                # Tạo đơn hàng
                cursor = db.execute(
                    '''INSERT INTO orders (customer_name, customer_phone, customer_address, total_amount, status, created_at) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (customer[0], customer[1], customer[2], total_amount, status, 
                     (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d %H:%M:%S'))
                )
                order_id = cursor.lastrowid
                
                # Thêm chi tiết đơn hàng
                for item in cart_items:
                    db.execute(
                        '''INSERT INTO order_items (order_id, product_id, quantity, price) 
                           VALUES (?, ?, ?, ?)''',
                        (order_id, item['id'], item['quantity'], item['price'])
                    )
                
                orders_created += 1
                
        db.commit()
        
        print(f"\n✅ Đã tạo {orders_created} đơn hàng mẫu!")
        
        # Thống kê
        stats = Order.get_statistics()
        print("\n📊 THỐNG KÊ:")
        print(f"   - Tổng đơn hàng: {stats['total']}")
        print(f"   - Chờ xử lý: {stats['pending']}")
        print(f"   - Đang xử lý: {stats['processing']}")
        print(f"   - Hoàn thành: {stats['completed']}")
        print(f"   - Doanh thu: {stats['revenue']:,.0f}₫")
        
        print("\n📅 THỐNG KÊ THEO THỜI GIAN:")
        print(f"   - Hôm nay: {Order.get_orders_today()} đơn")
        print(f"   - Tuần này: {Order.get_orders_this_week()} đơn")
        print(f"   - Tháng này: {Order.get_orders_this_month()} đơn")
        
        top_products = Order.get_top_products(5)
        if top_products:
            print("\n🔥 TOP SẢN PHẨM BÁN CHẠY:")
            for i, product in enumerate(top_products, 1):
                print(f"   {i}. {product['name']}: {product['total_sold']} đã bán - {product['revenue']:,.0f}₫")
        
        print("\n" + "="*60)
        print("✅ HOÀN TẤT! Bạn có thể test dashboard ngay bây giờ")
        print("="*60)
        print("\nChạy: python admin_app.py")
        print("Truy cập: http://localhost:5001\n")

if __name__ == '__main__':
    try:
        add_sample_orders()
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()