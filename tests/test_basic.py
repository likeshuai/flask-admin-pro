"""
Basic tests for flask-admin-pro
"""
import pytest
from flask import Flask


def test_import():
    """Test that the package can be imported"""
    import flask_admin_pro
    assert hasattr(flask_admin_pro, 'AdminPro')
    assert hasattr(flask_admin_pro, 'create_admin')
    assert hasattr(flask_admin_pro, '__version__')


def test_admin_pro_creation():
    """Test AdminPro class instantiation"""
    from flask_admin_pro import AdminPro
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    admin = AdminPro()
    assert admin is not None
    assert admin.url_prefix == '/__admin__'


def test_create_admin_factory():
    """Test create_admin factory function"""
    from flask_admin_pro import create_admin
    
    admin = create_admin()
    assert admin is not None
    assert isinstance(admin.url_prefix, str)


def test_registry():
    """Test model registry"""
    from flask_admin_pro.core import registry
    
    assert registry is not None
    assert hasattr(registry, 'register')
    assert hasattr(registry, 'get_model')
    assert hasattr(registry, 'get_all_models')
