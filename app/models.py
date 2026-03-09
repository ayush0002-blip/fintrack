from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


# ─────────────────────────────────────────────────────────────
# User Loader (required by Flask-Login)
# ─────────────────────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ─────────────────────────────────────────────────────────────
# User Model
# ─────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(128), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # ── Relationships (added as features are built) ──────────
    # transactions  = db.relationship('Transaction', backref='user', lazy='dynamic')
    # budgets       = db.relationship('Budget',      backref='user', lazy='dynamic')

    # ── Password helpers ────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # ── Dunder ───────────────────────────────────────────────
    def __repr__(self) -> str:
        return f'<User id={self.id} email={self.email!r}>'
