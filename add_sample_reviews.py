"""
Script thêm đánh giá mẫu
Chạy: python add_sample_reviews.py
"""

from app import app
from models import Product, Review
import random

def add_sample_reviews():
    """Thêm đánh giá mẫu"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("⭐ THÊM ĐÁNH GIÁ MẪU")
        print("="*60 + "\n")
        
        # Lấy danh sách sản phẩm
        products = Product.get_all()
        
        if not products:
            print("❌ Không có sản phẩm nào!")
            return
        
        print(f"✅ Tìm thấy {len(products)} sản phẩm\n")
        
        # Danh sách tên khách hàng
        customer_names = [
            "Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường",
            "Phạm Thị Dung", "Hoàng Văn Em", "Đỗ Thị Phương",
            "Vũ Văn Giang", "Bùi Thị Hà", "Đinh Văn Hùng",
            "Ngô Thị Linh", "Dương Văn Minh", "Mai Thị Nga"
        ]
        
        # Nhận xét mẫu theo rating
        comments = {
            5: [
                "Món ăn rất ngon, đúng khẩu vị! Sẽ quay lại lần sau.",
                "Tuyệt vời! Chất lượng vượt mong đợi.",
                "Rất hài lòng, phục vụ nhanh, đồ ăn ngon.",
                "10 điểm cho món này! Quá tuyệt vời!",
                "Ngon không chê vào đâu được! Highly recommended!"
            ],
            4: [
                "Món ăn ngon, nhưng hơi lâu một chút.",
                "Chất lượng tốt, giá hợp lý.",
                "Ngon nhưng phần hơi ít.",
                "Đáng thử, khá ổn.",
                "Khá ngon, sẽ ủng hộ tiếp."
            ],
            3: [
                "Bình thường, không có gì đặc biệt.",
                "Tạm được, giá hơi cao.",
                "Ăn được, nhưng không xuất sắc lắm.",
                "Bình thường thôi.",
                "OK, nhưng có thể cải thiện hơn."
            ],
            2: [
                "Không được như kỳ vọng.",
                "Hơi thất vọng về chất lượng.",
                "Không ngon lắm.",
                "Cần cải thiện nhiều.",
                "Không như hình."
            ],
            1: [
                "Rất thất vọng!",
                "Không nên thử.",
                "Chất lượng kém.",
                "Không đúng như mô tả.",
                "Tệ!"
            ]
        }
        
        reviews_created = 0
        
        # Thêm 2-5 reviews cho mỗi sản phẩm
        for product in products:
            num_reviews = random.randint(2, 5)
            
            for _ in range(num_reviews):
                # Random rating (thiên về 4-5 sao nhiều hơn)
                rating = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[5, 10, 15, 30, 40]
                )[0]
                
                # Random tên khách hàng
                customer_name = random.choice(customer_names)
                
                # Random comment
                comment = random.choice(comments[rating])
                
                # Tạo review
                Review.create(product['id'], customer_name, rating, comment)
                reviews_created += 1
        
        print(f"\n✅ Đã tạo {reviews_created} đánh giá!")
        
        # Thống kê
        review_stats = Review.get_statistics()
        print("\n📊 THỐNG KÊ ĐÁNH GIÁ:")
        print(f"   - Tổng đánh giá: {review_stats['total']}")
        print(f"   - Điểm trung bình: {review_stats['average']}/5")
        print(f"   - Phân bổ:")
        for rating in range(5, 0, -1):
            stars = '⭐' * rating
            count = review_stats['distribution'][rating]
            print(f"      {stars} ({rating}): {count} đánh giá")
        
        print("\n" + "="*60)
        print("✅ HOÀN TẤT!")
        print("="*60)
        print("\nBạn có thể:")
        print("1. Xem trang sản phẩm: http://localhost:5000/product/1")
        print("2. Xem quản lý đánh giá: http://localhost:5001/reviews")
        print()

if __name__ == '__main__':
    try:
        add_sample_reviews()
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()