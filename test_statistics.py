"""
Script test các hàm thống kê
Chạy: python test_statistics.py
"""

from app import app
from models import Order, Product

def test_statistics():
    """Test tất cả hàm thống kê"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("🧪 TEST CÁC HÀM THỐNG KÊ")
        print("="*60 + "\n")
        
        # 1. Test get_statistics
        print("1️⃣  Test get_statistics()...")
        try:
            stats = Order.get_statistics()
            print(f"   ✅ Tổng đơn: {stats['total']}")
            print(f"   ✅ Chờ xử lý: {stats['pending']}")
            print(f"   ✅ Đang xử lý: {stats['processing']}")
            print(f"   ✅ Hoàn thành: {stats['completed']}")
            print(f"   ✅ Đã hủy: {stats['cancelled']}")
            print(f"   ✅ Doanh thu: {stats['revenue']:,.0f}₫")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
        
        # 2. Test orders theo thời gian
        print("\n2️⃣  Test orders theo thời gian...")
        try:
            today = Order.get_orders_today()
            week = Order.get_orders_this_week()
            month = Order.get_orders_this_month()
            print(f"   ✅ Hôm nay: {today} đơn")
            print(f"   ✅ Tuần này: {week} đơn")
            print(f"   ✅ Tháng này: {month} đơn")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
        
        # 3. Test revenue by date
        print("\n3️⃣  Test get_revenue_by_date(7)...")
        try:
            revenue_data = Order.get_revenue_by_date(7)
            print(f"   ✅ Có {len(revenue_data)} ngày dữ liệu")
            for row in revenue_data:
                print(f"      {row['date']}: {row['revenue']:,.0f}₫")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
        
        # 4. Test orders by status
        print("\n4️⃣  Test get_orders_by_status()...")
        try:
            status_data = Order.get_orders_by_status()
            print(f"   ✅ Có {len(status_data)} trạng thái")
            for row in status_data:
                print(f"      {row['status']}: {row['count']} đơn")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
        
        # 5. Test top products
        print("\n5️⃣  Test get_top_products(5)...")
        try:
            top_products = Order.get_top_products(5)
            print(f"   ✅ Có {len(top_products)} sản phẩm")
            for i, product in enumerate(top_products, 1):
                print(f"      {i}. {product['name']}")
                print(f"         - Đã bán: {product['total_sold']}")
                print(f"         - Doanh thu: {product['revenue']:,.0f}₫")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
        
        # 6. Test API endpoints
        print("\n6️⃣  Test API endpoints...")
        from admin_app import app as admin_app
        client = admin_app.test_client()
        
        # Login trước
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        endpoints = [
            '/api/revenue-chart?days=7',
            '/api/status-chart',
            '/api/top-products-chart?limit=5'
        ]
        
        for endpoint in endpoints:
            try:
                response = client.get(endpoint)
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"   ✅ {endpoint}")
                    print(f"      Status: {response.status_code}")
                    print(f"      Data keys: {list(data.keys())}")
                else:
                    print(f"   ❌ {endpoint} - Status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {e}")
        
        print("\n" + "="*60)
        print("✅ KIỂM TRA HOÀN TẤT!")
        print("="*60)
        
        # Đề xuất
        if stats['total'] == 0:
            print("\n⚠️  CẢNH BÁO: Không có đơn hàng nào!")
            print("Chạy lệnh sau để thêm dữ liệu mẫu:")
            print("   python add_sample_orders.py")
        elif stats['completed'] == 0:
            print("\n⚠️  CẢNH BÁO: Không có đơn hàng hoàn thành!")
            print("Biểu đồ có thể trống vì chỉ tính đơn hàng đã hoàn thành.")
            print("Chạy lệnh sau để thêm dữ liệu mẫu:")
            print("   python add_sample_orders.py")
        else:
            print("\n✅ Dữ liệu OK! Dashboard sẽ hiển thị đầy đủ.")
        
        print()

if __name__ == '__main__':
    test_statistics()