"""
AdminPro models definition.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class AdminUserMixin:
    """Admin user model mixin."""
    
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
