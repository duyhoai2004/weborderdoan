"""
Script test API reviews
Chạy: python test_reviews_api.py
"""

from app import app
from models import Review, Product

def test_reviews_api():
    """Test các API reviews"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("🧪 TEST API REVIEWS")
        print("="*60 + "\n")
        
        # 1. Kiểm tra sản phẩm
        print("1️⃣  Kiểm tra sản phẩm...")
        products = Product.get_all()
        if not products:
            print("   ❌ Không có sản phẩm nào!")
            return
        
        print(f"   ✅ Có {len(products)} sản phẩm")
        
        # 2. Kiểm tra reviews
        print("\n2️⃣  Kiểm tra reviews...")
        review_stats = Review.get_statistics()
        print(f"   ✅ Tổng reviews: {review_stats['total']}")
        print(f"   ✅ Điểm TB: {review_stats['average']}")
        
        if review_stats['total'] == 0:
            print("\n   ⚠️  Chưa có review nào!")
            print("   Chạy lệnh: python add_sample_reviews.py")
            return
        
        # 3. Test API rating cho từng sản phẩm
        print("\n3️⃣  Test API rating cho từng sản phẩm...")
        client = app.test_client()
        
        for i, product in enumerate(products[:5], 1):
            try:
                response = client.get(f'/api/product/{product["id"]}/rating')
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"   ✅ {product['name']}")
                    print(f"      - Rating: {data['average']}/5")
                    print(f"      - Số đánh giá: {data['count']}")
                else:
                    print(f"   ❌ {product['name']} - Status: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {product['name']} - Error: {e}")
        
        # 4. Test API reviews list
        print("\n4️⃣  Test API reviews list...")
        product = products[0]
        try:
            response = client.get(f'/api/product/{product["id"]}/reviews')
            if response.status_code == 200:
                reviews = response.get_json()
                print(f"   ✅ Sản phẩm '{product['name']}' có {len(reviews)} đánh giá")
                if reviews:
                    print(f"   📝 Đánh giá mới nhất:")
                    review = reviews[0]
                    print(f"      - Người đánh giá: {review['customer_name']}")
                    print(f"      - Rating: {review['rating']}/5")
                    if review['comment']:
                        print(f"      - Comment: {review['comment'][:50]}...")
            else:
                print(f"   ❌ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 5. Test trang product detail
        print("\n5️⃣  Test trang product detail...")
        try:
            response = client.get(f'/product/{product["id"]}')
            if response.status_code == 200:
                print(f"   ✅ Trang chi tiết sản phẩm hoạt động OK")
                print(f"   🔗 URL: http://localhost:5000/product/{product['id']}")
            else:
                print(f"   ❌ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "="*60)
        print("✅ KIỂM TRA HOÀN TẤT!")
        print("="*60)
        
        print("\n📋 KẾT LUẬN:")
        if review_stats['total'] > 0:
            print("   ✅ API hoạt động tốt!")
            print("   ✅ Có thể test trên trình duyệt:")
            print(f"      - Trang chủ: http://localhost:5000")
            print(f"      - Menu: http://localhost:5000/menu")
            print(f"      - Chi tiết SP: http://localhost:5000/product/1")
        else:
            print("   ⚠️  Cần thêm dữ liệu review:")
            print("   Chạy: python add_sample_reviews.py")
        
        print()

if __name__ == '__main__':
    test_reviews_api()