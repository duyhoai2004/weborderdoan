from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import init_db, close_db
from models import Product, Order, Review

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production-12345'
app.config['SESSION_TYPE'] = 'filesystem'

# Đăng ký hàm đóng database
app.teardown_appcontext(close_db)

@app.route('/')
def index():
    """Trang chủ"""
    products = Product.get_all()[:8]  # Lấy 8 sản phẩm mới nhất
    categories = Product.get_categories()
    return render_template('customer/index.html', products=products, categories=categories)

@app.route('/menu')
def menu():
    """Trang thực đơn"""
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    if search:
        products = Product.search(search)
    elif category:
        products = Product.get_by_category(category)
    else:
        products = Product.get_all()
    
    categories = Product.get_categories()
    return render_template('customer/menu.html', 
                         products=products, 
                         categories=categories, 
                         selected_category=category,
                         search_query=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Chi tiết sản phẩm"""
    product = Product.get_by_id(product_id)
    if not product:
        return redirect(url_for('menu'))
    
    # Lấy sản phẩm cùng danh mục
    related_products = Product.get_by_category(product['category'])
    related_products = [p for p in related_products if p['id'] != product_id][:4]
    
    # Lấy rating
    rating_info = Review.get_average_rating(product_id)
    
    return render_template('customer/product_detail.html', 
                         product=product,
                         related_products=related_products,
                         rating_info=rating_info)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Thêm sản phẩm vào giỏ hàng"""
    try:
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Số lượng không hợp lệ'})
        
        product = Product.get_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Sản phẩm không tồn tại'})
        
        # Khởi tạo giỏ hàng nếu chưa có
        if 'cart' not in session:
            session['cart'] = []
        
        cart = session['cart']
        
        # Kiểm tra sản phẩm đã có trong giỏ hàng chưa
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
        
        # Tính tổng số lượng items trong giỏ
        total_items = sum(item['quantity'] for item in cart)
        
        return jsonify({
            'success': True, 
            'message': f'Đã thêm {quantity} sản phẩm vào giỏ hàng',
            'cart_count': len(cart),
            'total_items': total_items
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cart')
def cart():
    """Trang giỏ hàng"""
    cart_items = session.get('cart', [])
    
    # Tính tổng tiền
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    shipping_fee = 0 if subtotal >= 100000 else 20000  # Miễn phí ship từ 100k
    total = subtotal + shipping_fee
    
    return render_template('customer/cart.html', 
                         cart_items=cart_items, 
                         subtotal=subtotal,
                         shipping_fee=shipping_fee,
                         total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Cập nhật số lượng sản phẩm trong giỏ hàng"""
    try:
        product_id = int(request.form.get('product_id'))
        action = request.form.get('action')  # increase, decrease, remove
        
        cart = session.get('cart', [])
        
        for item in cart:
            if item['id'] == product_id:
                if action == 'increase':
                    item['quantity'] += 1
                elif action == 'decrease':
                    item['quantity'] -= 1
                    if item['quantity'] <= 0:
                        cart.remove(item)
                elif action == 'remove':
                    cart.remove(item)
                break
        
        session['cart'] = cart
        session.modified = True
        
        return redirect(url_for('cart'))
    
    except Exception as e:
        print(f"Error updating cart: {e}")
        return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Trang thanh toán"""
    cart_items = session.get('cart', [])
    
    if not cart_items:
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        try:
            customer_name = request.form.get('customer_name', '').strip()
            customer_phone = request.form.get('customer_phone', '').strip()
            customer_address = request.form.get('customer_address', '').strip()
            
            # Validate
            if not all([customer_name, customer_phone, customer_address]):
                return render_template('customer/checkout.html', 
                                     cart_items=cart_items,
                                     error='Vui lòng điền đầy đủ thông tin')
            
            # Tạo đơn hàng
            order_id = Order.create(customer_name, customer_phone, customer_address, cart_items)
            
            # Xóa giỏ hàng
            session.pop('cart', None)
            
            return redirect(url_for('checkout_success', order_id=order_id))
        
        except Exception as e:
            return render_template('customer/checkout.html', 
                                 cart_items=cart_items,
                                 error=f'Có lỗi xảy ra: {str(e)}')
    
    # GET request
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    shipping_fee = 0 if subtotal >= 100000 else 20000
    total = subtotal + shipping_fee
    
    return render_template('customer/checkout.html', 
                         cart_items=cart_items,
                         subtotal=subtotal,
                         shipping_fee=shipping_fee,
                         total=total)

@app.route('/checkout/success/<int:order_id>')
def checkout_success(order_id):
    """Trang thành công sau khi đặt hàng"""
    order, items = Order.get_by_id(order_id)
    
    if not order:
        return redirect(url_for('index'))
    
    return render_template('customer/checkout_success.html', 
                         order=order, 
                         items=items)

@app.route('/clear_cart')
def clear_cart():
    """Xóa toàn bộ giỏ hàng"""
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/review/add', methods=['POST'])
def add_review():
    """Thêm đánh giá cho sản phẩm"""
    try:
        product_id = int(request.form.get('product_id'))
        customer_name = request.form.get('customer_name', '').strip()
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment', '').strip()
        order_id = request.form.get('order_id')
        
        # Validate
        if not customer_name or not (1 <= rating <= 5):
            return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'})
        
        # Tạo review
        Review.create(product_id, customer_name, rating, comment, order_id)
        
        return jsonify({
            'success': True, 
            'message': 'Cảm ơn bạn đã đánh giá!'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/reviews')
def reviews():
    """Trang tất cả đánh giá"""
    all_reviews = Review.get_all()
    return render_template('customer/reviews.html', reviews=all_reviews)

@app.route('/api/product/<int:product_id>/rating')
def api_product_rating(product_id):
    """API lấy rating của sản phẩm"""
    try:
        rating_info = Review.get_average_rating(product_id)
        return jsonify(rating_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/product/<int:product_id>/reviews')
def api_product_reviews(product_id):
    """API lấy danh sách reviews của sản phẩm"""
    try:
        reviews = Review.get_by_product(product_id)
        return jsonify([dict(review) for review in reviews])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000, host='0.0.0.0')