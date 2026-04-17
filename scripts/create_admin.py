import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        email = "admin@fintrack.com"
        password = "admin123"
        
        # Check if already exists
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User {email} already exists. Updating to admin...")
            user.is_admin = True
        else:
            print(f"Creating admin user: {email}")
            user = User(
                full_name="System Admin",
                email=email,
                is_admin=True
            )
            user.set_password(password)
            db.session.add(user)
        
        db.session.commit()
        print(f"Successfully created/updated admin: {email}")
        print(f"Password: {password}")

if __name__ == "__main__":
    create_admin()
