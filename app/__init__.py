from flask import Flask
from config import config
from app.extensions import db, login_manager

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transactions_bp
    from app.routes.analytics import analytics_bp
    from app.routes.budgets import budgets_bp
    from app.routes.subscriptions import subscriptions_bp
    from app.routes.settings import settings_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(budgets_bp, url_prefix='/budgets')
    app.register_blueprint(subscriptions_bp, url_prefix='/subscriptions')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    return app
