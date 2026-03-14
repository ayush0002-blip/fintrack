from datetime import date, timedelta
from decimal import Decimal
from app.models import Subscription

class SubscriptionService:
    @staticmethod
    def get_monthly_total(user):
        """
        Calculate the normalized monthly cost of all active subscriptions.
        Weekly: amount * 4.33
        Yearly: amount / 12
        Monthly: amount
        """
        total = Decimal('0.00')
        active_subs = user.subscriptions.filter_by(status=Subscription.STATUS_ACTIVE).all()
        
        for sub in active_subs:
            if sub.billing_cycle == Subscription.CYCLE_WEEKLY:
                total += sub.amount * Decimal('4.33')
            elif sub.billing_cycle == Subscription.CYCLE_YEARLY:
                total += sub.amount / Decimal('12.0')
            else:
                total += sub.amount
                
        return total.quantize(Decimal('0.01'))

    @staticmethod
    def get_upcoming_count(user, days=7):
        """Get count of subscriptions due within the specified number of days."""
        today = date.today()
        future = today + timedelta(days=days)
        
        return user.subscriptions.filter(
            Subscription.status == Subscription.STATUS_ACTIVE,
            Subscription.next_due_date >= today,
            Subscription.next_due_date <= future
        ).count()

    @staticmethod
    def enrich_subscription(sub):
        """Add metadata like 'days_remaining' and 'is_upcoming' to a subscription object."""
        today = date.today()
        delta = (sub.next_due_date - today).days
        
        sub.days_remaining = delta
        sub.is_upcoming = 0 <= delta <= 7
        sub.is_overdue = delta < 0
        
        return sub

    @classmethod
    def get_all_enriched(cls, user):
        """Fetch all subscriptions and enrich them."""
        subs = user.subscriptions.order_by(Subscription.next_due_date.asc()).all()
        return [cls.enrich_subscription(s) for s in subs]
