from app import app
from database import init_db
import os

if __name__ == '__main__':
    # Kiểm tra và tao database nếu chưa tồn tại
    if not os.path.exists('food_ordering.db'):
        with app.app_context():
            init_db()
            print("Database created successfully.")

    print("Starting the Flask application...")
    print("Access the application at http://localhost:5000")
    print("Admin page at http://localhost:5000/admin")
    app.run(debug=True, host='0.0.0.0', port=5000)