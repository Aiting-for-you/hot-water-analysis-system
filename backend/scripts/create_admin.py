import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User

def create_admin_user():
    """
    Creates the initial 'admin' user if it doesn't exist.
    Uses predefined credentials and is non-interactive.
    """
    app = create_app()
    with app.app_context():
        # Check if the admin user already exists
        if User.query.filter_by(username='admin').first():
            print("Admin user already exists. No action taken.")
            return

        # Create the admin user with default credentials
        print("Admin user not found. Creating a new one with default credentials...")
        admin_user = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin_user.set_password('adminpassword')  # Set the default password
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("="*40)
        print("Admin user created successfully!")
        print("  Username: admin")
        print("  Password: adminpassword")
        print("="*40)
        print("You can now log in with these credentials.")

if __name__ == '__main__':
    create_admin_user() 