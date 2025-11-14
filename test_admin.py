"""
Script test để kiểm tra admin app
Chạy: python test_admin.py
"""

import os
import sys

print("=" * 60)
print("KIỂM TRA ADMIN APP")
print("=" * 60)

# 1. Kiểm tra các file cần thiết
print("\n1. Kiểm tra các file...")
required_files = [
    'admin_app.py',
    'database.py',
    'models.py',
    'templates/admin/login.html',
    'templates/admin/base.html',
    'templates/admin/dashboard.html'
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - KHÔNG TỒN TẠI")
        missing_files.append(file)

if missing_files:
    print(f"\n❌ Thiếu {len(missing_files)} file(s)!")
    sys.exit(1)

# 2. Kiểm tra import
print("\n2. Kiểm tra import...")
try:
    from admin_app import app
    print("   ✅ Import admin_app thành công")
except Exception as e:
    print(f"   ❌ Lỗi import: {e}")
    sys.exit(1)

# 3. Kiểm tra routes
print("\n3. Kiểm tra routes...")
routes = []
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        routes.append(f"{rule.endpoint}: {rule.rule}")
        print(f"   ✅ {rule.endpoint}: {rule.rule}")

if not routes:
    print("   ❌ Không có route nào!")
    sys.exit(1)

# 4. Test Flask app context
print("\n4. Test Flask context...")
try:
    with app.app_context():
        from database import init_db
        init_db()
    print("   ✅ Database khởi tạo thành công")
except Exception as e:
    print(f"   ❌ Lỗi database: {e}")
    sys.exit(1)

# 5. Test routes
print("\n5. Test routes...")
test_routes = [
    '/login',
    '/',
    '/products',
    '/orders'
]

client = app.test_client()

for route in test_routes:
    try:
        response = client.get(route, follow_redirects=False)
        if response.status_code in [200, 302]:
            print(f"   ✅ {route} - Status: {response.status_code}")
        else:
            print(f"   ⚠️  {route} - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ {route} - Lỗi: {e}")

# 6. Test login
print("\n6. Test login...")
try:
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    if response.status_code == 200:
        print("   ✅ Login thành công")
        
        # Test dashboard sau khi login
        response = client.get('/')
        if response.status_code == 200:
            print("   ✅ Dashboard accessible")
        else:
            print(f"   ❌ Dashboard error: {response.status_code}")
    else:
        print(f"   ❌ Login failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Lỗi test login: {e}")

print("\n" + "=" * 60)
print("✅ KIỂM TRA HOÀN TẤT!")
print("=" * 60)
print("\nNếu tất cả đều OK, hãy chạy:")
print("   python admin_app.py")
print("\nHoặc:")
print("   python run.py")
print()