import os
import sys
import getpass

# Add project root to the Python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User

def create_admin_user(username, password, email):
    """Creates an admin user."""
    app = create_app()
    with app.app_context():
        # Check if the user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            print(f"User with username '{username}' or email '{email}' already exists.")
            return

        # Create a new admin user
        admin_user = User(
            username=username,
            email=email,
            role='admin'
        )
        admin_user.set_password(password)  # Hash the password

        db.session.add(admin_user)
        db.session.commit()
        print("-" * 50)
        print(f"Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("-" * 50)

if __name__ == '__main__':
    # Use fixed credentials for non-interactive execution
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "adminpassword"
    ADMIN_EMAIL = "admin@example.com"
    
    print("Creating admin user with predefined credentials...")
    create_admin_user(ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL) 