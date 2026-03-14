import os
import sys
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User, Transaction, Budget, Subscription

def seed_demo_data():
    app = create_app()
    with app.app_context():
        print("Starting demo data seeding...")
        
        # 1. Create or get Demo User
        demo_email = "demo@fintrack.com"
        user = User.query.filter_by(email=demo_email).first()
        
        if user:
            print(f"User {demo_email} already exists. Cleaning up old data...")
            # Clear existing data for a fresh start
            Transaction.query.filter_by(user_id=user.id).delete()
            Budget.query.filter_by(user_id=user.id).delete()
            Subscription.query.filter_by(user_id=user.id).delete()
        else:
            print(f"Creating new user: {demo_email}")
            user = User(
                full_name="Demo User",
                email=demo_email
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.flush() # Get user ID
            
        # 2. Add Realistic Transactions (Last 6 Months)
        print("Generating transactions...")
        today = date.today()
        
        categories = Transaction.CATEGORIES
        
        # Income sources
        income_sources = [
            ("Monthly Salary", "Salary", 45000.00),
            ("Freelance Project", "Freelance", 12000.00),
            ("Dividend Payout", "Investment", 2500.00)
        ]
        
        # Expense categories and typical items
        expense_items = {
            "Food & Dining": ["Restuarant", "Groceries", "Coffee Shop", "Zomato", "Swiggy"],
            "Transport": ["Petrol", "Uber Ride", "Bus Pass", "Auto Rickshaw"],
            "Housing": ["Rent", "Electricity Bill", "Water Bill", "Internet"],
            "Healthcare": ["Pharmacy", "Doctor Visit", "Hospital"],
            "Entertainment": ["Movie Tickets", "Gaming Console", "Concert"],
            "Shopping": ["Amazon Purchase", "Nike Store", "H&M", "Local Market"],
            "Education": ["Online Course", "Bookstore", "Workshop"],
            "Other": ["Laundry", "Haircut", "Gifts"]
        }

        for i in range(180): # Approx 6 months
            current_date = today - timedelta(days=i)
            
            # Monthly Salary (1st of month)
            if current_date.day == 1:
                db.session.add(Transaction(
                    user_id=user.id,
                    title="Monthly Salary",
                    amount=Decimal("45000.00"),
                    type="income",
                    category="Salary",
                    date=current_date
                ))
            
            # Rent (5th of month)
            if current_date.day == 5:
                db.session.add(Transaction(
                    user_id=user.id,
                    title="Monthly Rent",
                    amount=Decimal("15000.00"),
                    type="expense",
                    category="Housing",
                    date=current_date
                ))

            # Random daily expenses
            num_expenses = random.randint(0, 3)
            for _ in range(num_expenses):
                cat = random.choice(list(expense_items.keys()))
                title = random.choice(expense_items[cat])
                amount = Decimal(str(round(random.uniform(50, 1500), 2)))
                
                db.session.add(Transaction(
                    user_id=user.id,
                    title=title,
                    amount=amount,
                    type="expense",
                    category=cat,
                    date=current_date
                ))

        # 3. Add Budgets for Current Month
        print("Generating budgets...")
        current_month = today.month
        current_year = today.year
        
        budget_configs = [
            ("Food & Dining", 8000.00),
            ("Transport", 3000.00),
            ("Shopping", 5000.00),
            ("Entertainment", 2000.00),
            ("Other", 1500.00)
        ]
        
        for cat, limit in budget_configs:
            db.session.add(Budget(
                user_id=user.id,
                category=cat,
                monthly_limit=Decimal(str(limit)),
                month=current_month,
                year=current_year
            ))

        # 4. Add Subscriptions
        print("Generating subscriptions...")
        subscriptions = [
            ("Netflix", 499.00, "monthly", today + timedelta(days=12)),
            ("Spotify", 119.00, "monthly", today + timedelta(days=5)),
            ("Amazon Prime", 1499.00, "yearly", today + timedelta(days=25)),
            ("Gym Membership", 1500.00, "monthly", today - timedelta(days=2)), # Overdue demo
            ("Github Copilot", 800.00, "monthly", today + timedelta(days=1)), # Upcoming demo
        ]
        
        for name, amt, cycle, due in subscriptions:
            db.session.add(Subscription(
                user_id=user.id,
                name=name,
                amount=Decimal(str(amt)),
                billing_cycle=cycle,
                next_due_date=due,
                status="active"
            ))

        db.session.commit()
        print("\nDemo data seeding completed successfully!")
        print("-" * 30)
        print("Credentials:")
        print(f"Email:    {demo_email}")
        print(f"Password: password123")
        print("-" * 30)

if __name__ == "__main__":
    seed_demo_data()
