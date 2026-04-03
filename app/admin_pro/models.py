"""
Database models for Flask Admin Pro.
"""

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import os


# Get timezone from environment variable or use local time by default
ADMIN_TIMEZONE = os.environ.get('ADMIN_TIMEZONE', 'local')


def now():
    """Return current time based on ADMIN_TIMEZONE setting.

    Set ADMIN_TIMEZONE environment variable to control timezone:
    - 'local' or not set: Use system local time (default)
    - 'utc': Use UTC time
    - 'Asia/Shanghai', 'America/New_York', etc.: Use specific timezone
    """
    if ADMIN_TIMEZONE == 'utc':
        return datetime.now(timezone.utc)
    elif ADMIN_TIMEZONE == 'local' or not ADMIN_TIMEZONE:
        # Use naive datetime for local time (compatible with SQLite)
        return datetime.now()
    else:
        # Try to use specific timezone
        try:
            import zoneinfo
            tz = zoneinfo.ZoneInfo(ADMIN_TIMEZONE)
            return datetime.now(tz)
        except Exception:
            # Fallback to local time if timezone not available
            return datetime.now()


# Keep utcnow for backward compatibility
def utcnow():
    """Return current UTC time with timezone info."""
    return datetime.now(timezone.utc)


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
    user_agent = None
    request_headers = None
    request_body = None
    response_body = None
    created_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'method': self.method,
            'path': self.path,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_headers': self.request_headers,
            'request_body': self.request_body,
            'response_body': self.response_body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AuditLogMixin:
    """Audit log model mixin for tracking user operations."""
    
    id = None
    user_id = None
    username = None
    action = None
    resource_type = None
    resource_id = None
    old_value = None
    new_value = None
    ip_address = None
    created_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class SystemConfigMixin:
    """System configuration model mixin."""
    
    id = None
    key = None
    value = None
    description = None
    category = None
    is_public = None
    created_at = None
    updated_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'category': self.category,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
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
        created_at = db.Column(db.DateTime, default=now)
        updated_at = db.Column(db.DateTime, default=now, onupdate=now)

        def __repr__(self):
            return f'<AdminUser {self.username}>'

    class RequestLog(RequestLogMixin, db.Model):
        __tablename__ = 'request_logs'
        
        id = db.Column(db.Integer, primary_key=True)
        method = db.Column(db.String(10), nullable=False)
        path = db.Column(db.String(500), nullable=False)
        status_code = db.Column(db.Integer)
        response_time = db.Column(db.Float)
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.String(500))
        request_headers = db.Column(db.Text)
        request_body = db.Column(db.Text)
        response_body = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=now, index=True)

        def __repr__(self):
            return f'<RequestLog {self.method} {self.path}>'

    class AuditLog(AuditLogMixin, db.Model):
        __tablename__ = 'audit_logs'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
        username = db.Column(db.String(80))
        action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
        resource_type = db.Column(db.String(100))  # Model name or resource type
        resource_id = db.Column(db.String(50))  # ID of the affected record
        old_value = db.Column(db.Text)  # JSON of old values
        new_value = db.Column(db.Text)  # JSON of new values
        ip_address = db.Column(db.String(45))
        created_at = db.Column(db.DateTime, default=now, index=True)

        def __repr__(self):
            return f'<AuditLog {self.action} {self.resource_type}>'

    class SystemConfig(SystemConfigMixin, db.Model):
        __tablename__ = 'system_configs'
        
        id = db.Column(db.Integer, primary_key=True)
        key = db.Column(db.String(100), unique=True, nullable=False, index=True)
        value = db.Column(db.Text)
        description = db.Column(db.String(255))
        category = db.Column(db.String(50), default='general')  # general, security, email, api
        is_public = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=now)
        updated_at = db.Column(db.DateTime, default=now, onupdate=now)

        def __repr__(self):
            return f'<SystemConfig {self.key}>'
    
    return AdminUser, RequestLog, AuditLog, SystemConfig
