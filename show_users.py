from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("\n--- Registered Users in Database ---")
    if not users:
        print("No users found in the database yet.")
    else:
        for user in users:
            print(f"ID: {user.id} | Name: {user.full_name} | Email: {user.email}")
    print("------------------------------------\n")
