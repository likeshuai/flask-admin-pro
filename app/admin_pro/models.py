"""
Database models for Flask Admin Pro.
"""

from datetime import datetime
from .model_mixins import AdminUserMixin, RequestLogMixin


def create_admin_models(db):
    """Create AdminPro models using the provided db instance."""
    
    class AdminUser(AdminUserMixin, db.Model):
        __tablename__ = 'admin_users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        email = db.Column(db.String(120))
        role = db.Column(db.String(20), default='admin')
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f'<AdminUser {self.username}>'

    class RequestLog(RequestLogMixin, db.Model):
        __tablename__ = 'request_logs'
        
        id = db.Column(db.Integer, primary_key=True)
        method = db.Column(db.String(10), nullable=False)
        path = db.Column(db.String(255), nullable=False)
        status_code = db.Column(db.Integer)
        response_time = db.Column(db.Float)
        ip_address = db.Column(db.String(45))
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        
        def __repr__(self):
            return f'<RequestLog {self.method} {self.path}>'
    
    return AdminUser, RequestLog
