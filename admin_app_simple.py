"""
Admin App phiên bản đơn giản để test
Chạy: python admin_app_simple.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'test-secret-key'

# Đăng nhập
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt: {username}")
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            session['username'] = username
            print("✅ Login successful!")
            return redirect(url_for('dashboard'))
        else:
            print("❌ Login failed!")
            flash('Sai tên đăng nhập hoặc mật khẩu!', 'danger')
    
    # Render inline HTML nếu không có template
    try:
        return render_template('admin/login.html')
    except:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Login</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container">
                <div class="row justify-content-center mt-5">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h4 class="mb-0">Admin Login</h4>
                            </div>
                            <div class="card-body">
                                ''' + (f'<div class="alert alert-danger">{flash("error")[0]}</div>' if flash("_flashes") else '') + '''
                                <form method="POST">
                                    <div class="mb-3">
                                        <label>Username</label>
                                        <input type="text" name="username" class="form-control" required>
                                    </div>
                                    <div class="mb-3">
                                        <label>Password</label>
                                        <input type="password" name="password" class="form-control" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">Login</button>
                                </form>
                                <div class="mt-3 text-muted small">
                                    Demo: admin / admin123
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''

@app.route('/')
@login_required
def dashboard():
    print("✅ Dashboard accessed!")
    
    # Render inline HTML nếu không có template
    try:
        from models import Product, Order
        stats = Order.get_statistics()
        total_products = len(Product.get_all())
        recent_orders = Order.get_all()[:5]
        
        return render_template('admin/dashboard.html',
                             stats=stats,
                             total_products=total_products,
                             recent_orders=recent_orders)
    except Exception as e:
        print(f"Dashboard error: {e}")
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar navbar-dark bg-dark">
                <div class="container-fluid">
                    <span class="navbar-brand">Admin Panel</span>
                    <a href="{url_for('logout')}" class="btn btn-outline-light btn-sm">Logout</a>
                </div>
            </nav>
            <div class="container mt-4">
                <h1>Dashboard</h1>
                <div class="alert alert-success">
                    ✅ Đăng nhập thành công! Username: {session.get('username')}
                </div>
                <div class="alert alert-info">
                    Nếu bạn thấy trang này, nghĩa là admin app đang hoạt động!
                </div>
                <div class="card">
                    <div class="card-body">
                        <h5>Thông tin</h5>
                        <p>Session: {dict(session)}</p>
                        <p>Error (if any): {e}</p>
                    </div>
                </div>
                <div class="mt-3">
                    <a href="http://localhost:5000" class="btn btn-primary" target="_blank">
                        Mở trang khách hàng
                    </a>
                </div>
            </div>
        </body>
        </html>
        '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔐 ADMIN APP SIMPLE - TESTING MODE")
    print("="*60)
    print("\n📍 URL: http://localhost:5001")
    print("👤 Username: admin")
    print("🔑 Password: admin123")
    print("\n⚡ Starting server...\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')