"""
Authentication manager for Flask Admin Pro.
"""

from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps


class AuthManager:
    """Handle authentication and authorization."""
    
    def __init__(self, app=None, AdminUser=None):
        self.app = app
        self.AdminUser = AdminUser
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
    
    def authenticate(self, username, password):
        if not self.AdminUser:
            return None
        
        user = self.AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            return user
        return None
    
    def login(self, user, remember=False):
        login_user(user, remember=remember)
    
    def logout(self):
        logout_user()
    
    def require_login(self, f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    
    def require_admin(self, f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role != 'admin':
                return {'error': 'Admin access required'}, 403
            return f(*args, **kwargs)
        return decorated_function
    
    def is_authenticated(self):
        return current_user.is_authenticated
    
    def get_current_user(self):
        return current_user if self.is_authenticated() else None
