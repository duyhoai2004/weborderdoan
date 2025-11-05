// Xử lý form thêm vào giỏ hàng
document.addEventListener('DOMContentLoaded', function() {
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    
    addToCartForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Hiển thị thông báo
                showAlert('Đã thêm vào giỏ hàng!', 'success');
                
                // Cập nhật số lượng trong giỏ hàng
                updateCartCount(result.cart_count);
            } else {
                showAlert(result.message, 'danger');
            }
        });
    });
});

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    // Tự động ẩn sau 3 giây
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function updateCartCount(count) {
    const cartBadge = document.querySelector('.badge');
    if (cartBadge) {
        cartBadge.textContent = count;
    }
}