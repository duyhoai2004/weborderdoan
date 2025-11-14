from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from database import init_db, close_db
from models import Product, Order
import traceback

app = Flask(__name__)
app.secret_key = 'admin-secret-key-change-in-production-67890'
app.config['SESSION_TYPE'] = 'filesystem'

# Đăng ký hàm đóng database
app.teardown_appcontext(close_db)

# Thông tin đăng nhập admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def login_required(f):
    """Decorator kiểm tra đăng nhập"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Vui lòng đăng nhập để tiếp tục!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập admin"""
    try:
        # Nếu đã đăng nhập, chuyển đến dashboard
        if 'admin_logged_in' in session:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"[LOGIN] Attempting login: {username}")  # Debug
            
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                flash('Đăng nhập thành công!', 'success')
                print("[LOGIN] Login successful!")  # Debug
                return redirect(url_for('dashboard'))
            else:
                flash('Sai tên đăng nhập hoặc mật khẩu!', 'danger')
                print("[LOGIN] Login failed!")  # Debug
        
        return render_template('admin/login.html')
    
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        traceback.print_exc()
        return f"Lỗi: {str(e)}", 500

@app.route('/logout')
def logout():
    """Đăng xuất"""
    session.clear()
    flash('Đã đăng xuất thành công!', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Dashboard admin"""
    try:
        print("[DASHBOARD] Loading dashboard...")  # Debug
        
        stats = Order.get_statistics()
        recent_orders = Order.get_all()[:10]
        total_products = len(Product.get_all())
        
        # Thống kê theo thời gian
        orders_today = Order.get_orders_today()
        orders_week = Order.get_orders_this_week()
        orders_month = Order.get_orders_this_month()
        
        # Top sản phẩm bán chạy
        top_products = Order.get_top_products(5)
        
        print(f"[DASHBOARD] Stats: {stats}")  # Debug
        
        return render_template('admin/dashboard.html',
                             stats=stats,
                             total_products=total_products,
                             recent_orders=recent_orders,
                             orders_today=orders_today,
                             orders_week=orders_week,
                             orders_month=orders_month,
                             top_products=top_products)
    
    except Exception as e:
        print(f"[ERROR] Dashboard error: {e}")
        traceback.print_exc()
        return f"Lỗi dashboard: {str(e)}", 500

@app.route('/products')
@login_required
def products():
    """Danh sách sản phẩm"""
    try:
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        if search:
            all_products = Product.search(search)
        elif category:
            all_products = Product.get_by_category(category)
        else:
            all_products = Product.get_all()
        
        categories = Product.get_categories()
        
        return render_template('admin/products.html', 
                             products=all_products,
                             categories=categories,
                             search_query=search,
                             selected_category=category)
    
    except Exception as e:
        print(f"[ERROR] Products error: {e}")
        traceback.print_exc()
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Thêm sản phẩm mới"""
    try:
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = float(request.form.get('price', 0))
            image_url = request.form.get('image_url', '').strip()
            category = request.form.get('category', '').strip()
            
            # Validate
            if not all([name, price, image_url, category]):
                flash('Vui lòng điền đầy đủ thông tin bắt buộc!', 'danger')
                return render_template('admin/product_form.html', product=None)
            
            if price <= 0:
                flash('Giá sản phẩm phải lớn hơn 0!', 'danger')
                return render_template('admin/product_form.html', product=None)
            
            Product.create(name, description, price, image_url, category)
            flash(f'Đã thêm sản phẩm "{name}" thành công!', 'success')
            return redirect(url_for('products'))
        
        return render_template('admin/product_form.html', product=None)
    
    except Exception as e:
        print(f"[ERROR] Add product error: {e}")
        traceback.print_exc()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
        return redirect(url_for('products'))

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Sửa sản phẩm"""
    try:
        product = Product.get_by_id(product_id)
        
        if not product:
            flash('Không tìm thấy sản phẩm!', 'danger')
            return redirect(url_for('products'))
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = float(request.form.get('price', 0))
            image_url = request.form.get('image_url', '').strip()
            category = request.form.get('category', '').strip()
            
            # Validate
            if not all([name, price, image_url, category]):
                flash('Vui lòng điền đầy đủ thông tin bắt buộc!', 'danger')
                return render_template('admin/product_form.html', product=product)
            
            if price <= 0:
                flash('Giá sản phẩm phải lớn hơn 0!', 'danger')
                return render_template('admin/product_form.html', product=product)
            
            Product.update(product_id, name, description, price, image_url, category)
            flash(f'Đã cập nhật sản phẩm "{name}" thành công!', 'success')
            return redirect(url_for('products'))
        
        return render_template('admin/product_form.html', product=product)
    
    except Exception as e:
        print(f"[ERROR] Edit product error: {e}")
        traceback.print_exc()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
        return redirect(url_for('products'))

@app.route('/products/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    """Xóa sản phẩm"""
    try:
        product = Product.get_by_id(product_id)
        
        if product:
            Product.delete(product_id)
            flash(f'Đã xóa sản phẩm "{product["name"]}" thành công!', 'success')
        else:
            flash('Không tìm thấy sản phẩm!', 'danger')
        
        return redirect(url_for('products'))
    
    except Exception as e:
        print(f"[ERROR] Delete product error: {e}")
        traceback.print_exc()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
        return redirect(url_for('products'))

@app.route('/orders')
@login_required
def orders():
    """Danh sách đơn hàng"""
    try:
        status_filter = request.args.get('status', '')
        
        if status_filter:
            all_orders = Order.get_by_status(status_filter)
        else:
            all_orders = Order.get_all()
        
        return render_template('admin/orders.html', 
                             orders=all_orders,
                             status_filter=status_filter)
    
    except Exception as e:
        print(f"[ERROR] Orders error: {e}")
        traceback.print_exc()
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """Chi tiết đơn hàng"""
    try:
        order, items = Order.get_by_id(order_id)
        
        if not order:
            flash('Không tìm thấy đơn hàng!', 'danger')
            return redirect(url_for('orders'))
        
        return render_template('admin/order_detail.html', 
                             order=order, 
                             items=items)
    
    except Exception as e:
        print(f"[ERROR] Order detail error: {e}")
        traceback.print_exc()
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('orders'))

@app.route('/orders/update_status', methods=['POST'])
@login_required
def update_order_status():
    """Cập nhật trạng thái đơn hàng"""
    try:
        order_id = int(request.form.get('order_id'))
        status = request.form.get('status')
        
        valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
        if status not in valid_statuses:
            flash('Trạng thái không hợp lệ!', 'danger')
            return redirect(url_for('order_detail', order_id=order_id))
        
        Order.update_status(order_id, status)
        
        status_names = {
            'pending': 'Chờ xử lý',
            'processing': 'Đang xử lý',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        
        flash(f'Đã cập nhật trạng thái đơn hàng #{order_id} thành "{status_names[status]}"!', 'success')
        return redirect(url_for('order_detail', order_id=order_id))
    
    except Exception as e:
        print(f"[ERROR] Update status error: {e}")
        traceback.print_exc()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
        return redirect(url_for('orders'))

@app.errorhandler(404)
def not_found(e):
    """Xử lý lỗi 404"""
    return render_template('admin/login.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Xử lý lỗi 500"""
    print(f"[ERROR] 500 error: {e}")
    traceback.print_exc()
    return f"Lỗi server: {str(e)}", 500

# API cho biểu đồ
@app.route('/api/revenue-chart')
@login_required
def api_revenue_chart():
    """API dữ liệu biểu đồ doanh thu"""
    try:
        days = request.args.get('days', 7, type=int)
        data = Order.get_revenue_by_date(days)
        
        result = {
            'labels': [row['date'] for row in data],
            'data': [float(row['revenue']) for row in data]
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status-chart')
@login_required
def api_status_chart():
    """API dữ liệu biểu đồ trạng thái"""
    try:
        data = Order.get_orders_by_status()
        
        status_labels = {
            'pending': 'Chờ xử lý',
            'processing': 'Đang xử lý',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        
        result = {
            'labels': [status_labels.get(row['status'], row['status']) for row in data],
            'data': [row['count'] for row in data]
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-products-chart')
@login_required
def api_top_products_chart():
    """API dữ liệu biểu đồ sản phẩm bán chạy"""
    try:
        limit = request.args.get('limit', 10, type=int)
        data = Order.get_top_products(limit)
        
        result = {
            'labels': [row['name'] for row in data],
            'data': [row['total_sold'] for row in data],
            'revenue': [float(row['revenue']) for row in data]
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔐 ADMIN APP - STARTING")
    print("="*60)
    print("\n📍 URL: http://localhost:5001")
    print("👤 Username: admin")
    print("🔑 Password: admin123")
    print("\n⚡ Đang khởi động server...\n")
    
    with app.app_context():
        try:
            init_db()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database error: {e}")
            traceback.print_exc()
    
    app.run(debug=True, port=5001, host='0.0.0.0')