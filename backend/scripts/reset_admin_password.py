import os
import sys
from getpass import getpass

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User

def reset_admin_password():
    """
    Resets the password for the 'admin' user.
    """
    app = create_app()
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()

        if not admin_user:
            print("Error: User 'admin' not found in the database.")
            choice = input("Would you like to create the 'admin' user? [y/N]: ").lower()
            if choice == 'y':
                email = input("Enter email for admin user: ")
                admin_user = User(username='admin', email=email, role='admin')
                db.session.add(admin_user)
                print("Admin user created. Now, please set the password.")
            else:
                return

        print("Resetting password for user 'admin'.")
        while True:
            password = getpass("Enter new password: ")
            password_confirm = getpass("Confirm new password: ")
            if password == password_confirm:
                if not password:
                    print("Password cannot be empty. Please try again.")
                    continue
                break
            else:
                print("Passwords do not match. Please try again.")

        admin_user.set_password(password)
        db.session.commit()
        print("Password for 'admin' has been successfully reset.")

if __name__ == '__main__':
    reset_admin_password() 