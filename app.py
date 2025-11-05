from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import init_db, get_db, close_db
from models import Product, Order
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Thay đổi key này trong production

# Đăng ký database
app.teardown_appcontext(close_db)

@app.route('/')
def index():
    products = Product.get_all()
    return render_template('index.html', products=products)

@app.route('/menu')
def menu():
    category = request.args.get('category', '')
    products = Product.get_all()
    
    if category:
        products = [p for p in products if p['category'] == category]
    
    categories = set([p['category'] for p in Product.get_all()])
    return render_template('menu.html', products=products, categories=categories, selected_category=category)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    
    product = Product.get_by_id(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'})
    
    # Khởi tạo giỏ hàng nếu chưa có
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    
    # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
    found = False
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += quantity
            found = True
            break
    
    # Nếu chưa có, thêm mới
    if not found:
        cart.append({
            'id': product_id,
            'name': product['name'],
            'price': product['price'],
            'image_url': product['image_url'],
            'quantity': quantity
        })
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({
        'success': True, 
        'message': 'Đã thêm vào giỏ hàng',
        'cart_count': len(cart)
    })

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    
    cart = session.get('cart', [])
    
    for item in cart:
        if item['id'] == product_id:
            if quantity <= 0:
                cart.remove(item)
            else:
                item['quantity'] = quantity
            break
    
    session['cart'] = cart
    session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_phone = request.form['customer_phone']
        customer_address = request.form['customer_address']
        
        cart_items = session.get('cart', [])
        if not cart_items:
            return redirect(url_for('cart'))
        
        # Tạo đơn hàng
        order_id = Order.create(customer_name, customer_phone, customer_address, cart_items)
        
        # Xóa giỏ hàng
        session.pop('cart', None)
        
        return render_template('checkout_success.html', order_id=order_id)
    
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('cart'))
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

# Admin routes
@app.route('/admin')
def admin_dashboard():
    orders = Order.get_all()
    products = Product.get_all()
    
    total_orders = len(orders)
    pending_orders = len([o for o in orders if o['status'] == 'pending'])
    total_products = len(products)
    
    return render_template('admin/dashboard.html', 
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         total_products=total_products,
                         recent_orders=orders[:5])

@app.route('/admin/products')
def admin_products():
    products = Product.get_all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
def admin_add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image_url = request.form['image_url']
        category = request.form['category']
        
        Product.create(name, description, price, image_url, category)
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image_url = request.form['image_url']
        category = request.form['category']
        
        Product.update(product_id, name, description, price, image_url, category)
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', product=product)

@app.route('/admin/products/delete/<int:product_id>')
def admin_delete_product(product_id):
    Product.delete(product_id)
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
def admin_orders():
    orders = Order.get_all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/orders/<int:order_id>')
def admin_order_detail(order_id):
    order, items = Order.get_by_id(order_id)
    if not order:
        return redirect(url_for('admin_orders'))
    
    return render_template('admin/order_detail.html', order=order, items=items)

@app.route('/admin/orders/update_status', methods=['POST'])
def admin_update_order_status():
    order_id = request.form['order_id']
    status = request.form['status']
    
    Order.update_status(order_id, status)
    return redirect(url_for('admin_order_detail', order_id=order_id))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)