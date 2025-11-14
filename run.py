#!/usr/bin/env python3
"""
Script để chạy cả 2 ứng dụng (Customer và Admin) cùng lúc
Sử dụng: python run.py
"""

import threading
import webbrowser
import time
import sys
import os

# Import các app
try:
    from app import app as customer_app
    from admin_app import app as admin_app
    from database import init_db
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    print("Vui lòng đảm bảo các file app.py và admin_app.py tồn tại!")
    sys.exit(1)

def print_banner():
    """In banner chào mừng"""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║         🍔 FOOD ORDER SYSTEM - DUAL MODE 🍔          ║
    ║                                                      ║
    ║           Hệ thống đặt món ăn trực tuyến            ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)

def run_customer_app():
    """Chạy ứng dụng khách hàng"""
    try:
        print("🚀 Đang khởi động CUSTOMER APP...")
        customer_app.run(
            debug=False,
            port=5000,
            host='0.0.0.0',
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Lỗi Customer App: {e}")

def run_admin_app():
    """Chạy ứng dụng admin"""
    try:
        print("🔐 Đang khởi động ADMIN APP...")
        admin_app.run(
            debug=False,
            port=5001,
            host='0.0.0.0',
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Lỗi Admin App: {e}")

def open_browsers():
    """Tự động mở trình duyệt"""
    time.sleep(3)  # Đợi server khởi động
    
    print("\n📱 Đang mở trình duyệt...")
    
    try:
        webbrowser.open('http://localhost:5000')
        time.sleep(1)
        webbrowser.open('http://localhost:5001')
        print("✅ Đã mở trình duyệt thành công!")
    except Exception as e:
        print(f"⚠️  Không thể tự động mở trình duyệt: {e}")
        print("Vui lòng mở thủ công:")
        print("   - Customer: http://localhost:5000")
        print("   - Admin:    http://localhost:5001")

def check_ports():
    """Kiểm tra xem các port đã được sử dụng chưa"""
    import socket
    
    ports_to_check = [5000, 5001]
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  CẢNH BÁO: Port {port} đang được sử dụng!")
            print(f"   Vui lòng đóng ứng dụng đang chạy trên port {port}")
            return False
    
    return True

def main():
    """Hàm chính"""
    print_banner()
    
    # Kiểm tra ports
    print("🔍 Kiểm tra ports...")
    if not check_ports():
        print("\n❌ Không thể khởi động. Vui lòng giải phóng các ports 5000 và 5001!")
        sys.exit(1)
    
    print("✅ Ports khả dụng!")
    
    # Khởi tạo database
    print("\n📦 Khởi tạo database...")
    try:
        with customer_app.app_context():
            init_db()
        print("✅ Database đã sẵn sàng!")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo database: {e}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 ĐANG KHỞI ĐỘNG CẢ 2 SERVER...")
    print("="*60)
    
    # Tạo threads
    customer_thread = threading.Thread(target=run_customer_app, daemon=True, name="CustomerApp")
    admin_thread = threading.Thread(target=run_admin_app, daemon=True, name="AdminApp")
    browser_thread = threading.Thread(target=open_browsers, daemon=True, name="Browser")
    
    # Khởi động threads
    customer_thread.start()
    admin_thread.start()
    browser_thread.start()
    
    # Đợi một chút để servers khởi động
    time.sleep(2)
    
    print("\n" + "="*60)
    print("✅ CẢ 2 ỨNG DỤNG ĐANG CHẠY THÀNH CÔNG!")
    print("="*60)
    print("\n📌 THÔNG TIN TRUY CẬP:")
    print("   👥 Khách hàng: http://localhost:5000")
    print("   🔐 Admin:      http://localhost:5001")
    print("      └─ Username: admin")
    print("      └─ Password: admin123")
    print("\n" + "="*60)
    print("⚠️  Nhấn Ctrl+C để dừng cả 2 server")
    print("="*60 + "\n")
    
    try:
        # Giữ main thread chạy
        while True:
            time.sleep(1)
            
            # Kiểm tra threads còn sống không
            if not customer_thread.is_alive() or not admin_thread.is_alive():
                print("\n⚠️  Phát hiện lỗi: Một trong các server đã dừng!")
                break
                
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("🛑 Đang dừng cả 2 server...")
        print("="*60)
        print("\n👋 Cảm ơn bạn đã sử dụng Food Order System!")
        print("   Hẹn gặp lại!\n")
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Lỗi nghiêm trọng: {e}")
        sys.exit(1)