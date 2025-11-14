#!/usr/bin/env python3
"""
Script kiểm tra cấu trúc thư mục và files
"""

import os
import sys

def print_tree(directory, prefix="", max_depth=3, current_depth=0):
    """In cấu trúc thư mục dạng tree"""
    if current_depth >= max_depth:
        return
    
    try:
        items = sorted(os.listdir(directory))
    except PermissionError:
        return
    
    # Lọc bỏ các thư mục không cần thiết
    ignore = ['__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules', '.idea']
    items = [item for item in items if item not in ignore and not item.startswith('.')]
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item}")
        
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            extension = "    " if is_last else "│   "
            print_tree(item_path, prefix + extension, max_depth, current_depth + 1)

def check_file_exists(filepath):
    """Kiểm tra file có tồn tại không"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists

def main():
    print("="*70)
    print(" 📁 KIỂM TRA CẤU TRÚC DỰ ÁN FOOD ORDER SYSTEM")
    print("="*70)
    
    # 1. Cấu trúc thư mục
    print("\n1️⃣  CẤU TRÚC THƯ MỤC:")
    print("-" * 70)
    print_tree(".", max_depth=3)
    
    # 2. Kiểm tra các file quan trọng
    print("\n2️⃣  KIỂM TRA CÁC FILE QUAN TRỌNG:")
    print("-" * 70)
    
    required_files = {
        "Backend": [
            "app.py",
            "admin_app.py",
            "database.py",
            "models.py",
            "run.py"
        ],
        "Customer Templates": [
            "templates/customer/base.html",
            "templates/customer/index.html",
            "templates/customer/menu.html",
            "templates/customer/cart.html",
            "templates/customer/checkout.html",
            "templates/customer/checkout_success.html"
        ],
        "Admin Templates": [
            "templates/admin/base.html",
            "templates/admin/login.html",
            "templates/admin/dashboard.html",
            "templates/admin/products.html",
            "templates/admin/product_form.html",
            "templates/admin/orders.html",
            "templates/admin/order_detail.html"
        ],
        "Other": [
            "requirements.txt",
            "README.md"
        ]
    }
    
    all_exist = True
    for category, files in required_files.items():
        print(f"\n📂 {category}:")
        for file in files:
            if not check_file_exists(file):
                all_exist = False
    
    # 3. Kiểm tra import
    print("\n3️⃣  KIỂM TRA IMPORT:")
    print("-" * 70)
    
    try:
        print("Đang test import app.py...", end=" ")
        from app import app as customer_app
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        all_exist = False
    
    try:
        print("Đang test import admin_app.py...", end=" ")
        from admin_app import app as admin_app
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        all_exist = False
    
    try:
        print("Đang test import models...", end=" ")
        from models import Product, Order
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
        all_exist = False
    
    # 4. Kiểm tra database
    print("\n4️⃣  KIỂM TRA DATABASE:")
    print("-" * 70)
    
    if os.path.exists("food_ordering.db"):
        size = os.path.getsize("food_ordering.db")
        print(f"✅ Database tồn tại (Kích thước: {size} bytes)")
    else:
        print("⚠️  Database chưa được tạo (sẽ tự động tạo khi chạy)")
    
    # Kết quả
    print("\n" + "="*70)
    if all_exist:
        print("✅ TẤT CẢ ĐỀU OK! Bạn có thể chạy:")
        print("\n   python run.py")
        print("\nHoặc:")
        print("   python app.py          # Customer app (port 5000)")
        print("   python admin_app.py    # Admin app (port 5001)")
    else:
        print("❌ CÓ LỖI! Vui lòng kiểm tra các file bị thiếu ở trên.")
        print("\nHướng dẫn:")
        print("1. Tạo thư mục templates/customer và templates/admin")
        print("2. Copy tất cả các file template vào đúng thư mục")
        print("3. Chạy lại script này để kiểm tra")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()