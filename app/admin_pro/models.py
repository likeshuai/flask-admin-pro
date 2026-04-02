"""
Database models for Flask Admin Pro.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class AdminUserMixin:
    """Admin user model mixin with Flask-Login compatibility."""
    
    id = None
    username = None
    password_hash = None
    email = None  
    role = None
    is_active = None
    created_at = None
    updated_at = None
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property  
    def is_anonymous(self):
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class RequestLogMixin:
    """Request log model mixin."""
    
    id = None
    method = None
    path = None
    status_code = None
    response_time = None
    ip_address = None
    created_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'method': self.method,
            'path': self.path,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


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
