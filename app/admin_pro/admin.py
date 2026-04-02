"""
Flask Admin Pro - Main Blueprint and initialization.
"""

import time
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from .models import db, AdminUser, RequestLog
from .core.auth import AuthManager
from .core.crud import CRUDManager
from .core.orm_adapter import ORMAdapter
from .core.monitor import MonitorManager


class AdminPro:
    """Flask Admin Pro main class."""
    
    def __init__(self, app=None, db=None, database_uri=None, **kwargs):
        self.app = app
        self.db = db
        self.database_uri = database_uri
        self.auth = AuthManager()
        self.crud = None
        self.adapter = None
        self.monitor = None
        
        if app is not None:
            self.init_app(app, db, database_uri, **kwargs)
    
    def init_app(self, app, db=None, database_uri=None, **kwargs):
        self.app = app
        self.database_uri = database_uri or app.config.get('ADMIN_DATABASE_URI', 'sqlite:///admin.db')
        
        app.config.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config.setdefault('ADMIN_DATABASE_URI', self.database_uri)
        app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        app.config.setdefault('ADMIN_USERNAME', 'admin')
        app.config.setdefault('ADMIN_PASSWORD', 'admin123')
        app.config.setdefault('ADMIN_ENABLE_MONITOR', True)
        
        # Always use internal db instance for AdminPro to avoid conflicts
        from .models import db as internal_db
        # Create a separate Flask app context for AdminPro if needed
        self.db = internal_db
        
        login_manager.init_app(app)
        csrf.init_app(app)
        
        self.crud = CRUDManager(self.db)
        self.adapter = ORMAdapter(self.db)
        self.monitor = MonitorManager(self.db)
        
        @login_manager.user_loader
        def load_user(user_id):
            return self.db.session.get(AdminUser, int(user_id))
        
        admin_bp = Blueprint('admin', __name__, 
                            url_prefix='/__admin__',
                            template_folder='templates',
                            static_folder='static')
        
        self._register_routes(admin_bp)
        csrf.exempt(admin_bp)
        
        app.register_blueprint(admin_bp)
        
        # Initialize AdminPro database separately
        with app.app_context():
            # Configure the internal db with AdminPro's database URI
            app.config['SQLALCHEMY_DATABASE_URI'] = self.database_uri
            self.db.init_app(app)
            self.db.create_all()
            self._create_default_admin(app)
            # Restore main app's database URI
            app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('MAIN_APP_DATABASE_URI', 'sqlite:///example.db')
        
        if app.config.get('ADMIN_ENABLE_MONITOR', True):
            @app.before_request
            def before_request():
                request.start_time = time.time()
            
            @app.after_request
            def after_request(response):
                if hasattr(request, 'start_time') and request.path.startswith('/__admin__/api/'):
                    response_time = (time.time() - request.start_time) * 1000
                    self.monitor.log_request(
                        method=request.method,
                        path=request.path,
                        status_code=response.status_code,
                        response_time=response_time,
                        ip_address=request.remote_addr,
                    )
                return response
    
    def _register_routes(self, bp):
        @bp.route('/')
        def index():
            if self.auth.is_authenticated():
                return render_template('admin/dashboard.html', user=self.auth.get_current_user())
            return redirect(url_for('admin.login'))
        
        @bp.route('/login')
        def login():
            if self.auth.is_authenticated():
                return redirect(url_for('admin.index'))
            return render_template('admin/login.html')
        
        @bp.route('/users')
        def users():
            if not self.auth.is_authenticated():
                return redirect(url_for('admin.login'))
            return render_template('admin/users.html', user=self.auth.get_current_user())
        
        @bp.route('/models')
        def models():
            if not self.auth.is_authenticated():
                return redirect(url_for('admin.login'))
            return render_template('admin/models.html', user=self.auth.get_current_user())
        
        @bp.route('/model/<name>')
        def model_detail(name):
            if not self.auth.is_authenticated():
                return redirect(url_for('admin.login'))
            model = self.adapter.get_model_by_name(name)
            if not model:
                return redirect(url_for('admin.models'))
            model_info = self.adapter.get_model_info(model)
            return render_template('admin/crud.html', 
                                 user=self.auth.get_current_user(),
                                 model_name=name,
                                 model_info=model_info)
        
        @bp.route('/monitor')
        def monitor():
            if not self.auth.is_authenticated():
                return redirect(url_for('admin.login'))
            return render_template('admin/monitor.html', user=self.auth.get_current_user())
        
        @bp.route('/api/login', methods=['POST'])
        def api_login():
            data = request.get_json() or {}
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'success': False, 'error': 'Username and password required'}), 400
            
            user = self.auth.authenticate(username, password)
            if user:
                self.auth.login(user, remember=True)
                return jsonify({'success': True, 'user': user.to_dict()})
            
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        @bp.route('/api/logout', methods=['POST'])
        def api_logout():
            self.auth.logout()
            return jsonify({'success': True})
        
        @bp.route('/api/me', methods=['GET'])
        def api_me():
            if not self.auth.is_authenticated():
                return jsonify({'authenticated': False})
            return jsonify({'authenticated': True, 'user': self.auth.get_current_user().to_dict()})
        
        @bp.route('/api/users', methods=['GET'])
        def api_get_users():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '')
            
            result = self.crud.get_all(AdminUser, page=page, per_page=per_page, search=search)
            return jsonify(result)
        
        @bp.route('/api/users', methods=['POST'])
        def api_create_user():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json() or {}
            
            if not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Username and password required'}), 400
            
            if self.db.session.query(AdminUser).filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already exists'}), 400
            
            user = AdminUser(
                username=data['username'],
                email=data.get('email'),
                role=data.get('role', 'admin'),
                is_active=data.get('is_active', True),
            )
            user.set_password(data['password'])
            
            self.db.session.add(user)
            self.db.session.commit()
            
            return jsonify({'success': True, 'user': user.to_dict()}), 201
        
        @bp.route('/api/users/<int:user_id>', methods=['PUT'])
        def api_update_user(user_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            user = self.db.session.get(AdminUser, user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            data = request.get_json() or {}
            
            if 'username' in data:
                existing = self.db.session.query(AdminUser).filter_by(username=data['username']).first()
                if existing and existing.id != user_id:
                    return jsonify({'error': 'Username already exists'}), 400
                user.username = data['username']
            
            if 'email' in data:
                user.email = data['email']
            
            if 'role' in data:
                user.role = data['role']
            
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            if 'password' in data and data['password']:
                user.set_password(data['password'])
            
            self.db.session.commit()
            
            return jsonify({'success': True, 'user': user.to_dict()})
        
        @bp.route('/api/users/<int:user_id>', methods=['DELETE'])
        def api_delete_user(user_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            user = self.db.session.get(AdminUser, user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if self.auth.get_current_user().id == user_id:
                return jsonify({'error': 'Cannot delete yourself'}), 400
            
            self.db.session.delete(user)
            self.db.session.commit()
            
            return jsonify({'success': True})
        
        @bp.route('/api/models', methods=['GET'])
        def api_get_models():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            models = []
            for model in self.adapter.get_models():
                if hasattr(model, '__tablename__') and not model.__name__.startswith('_'):
                    model_info = self.adapter.get_model_info(model)
                    if model_info:
                        models.append({
                            'name': model.__name__,
                            'table': model.__tablename__,
                        })
            
            return jsonify({'models': models})
        
        @bp.route('/api/models/<model_name>', methods=['GET'])
        def api_get_model_data(model_name):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            model = self.adapter.get_model_by_name(model_name)
            if not model:
                return jsonify({'error': 'Model not found'}), 404
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '')
            sort_by = request.args.get('sort_by', 'id')
            sort_order = request.args.get('sort_order', 'desc')
            
            result = self.crud.get_all(model, page=page, per_page=per_page, 
                                       search=search, sort_by=sort_by, sort_order=sort_order)
            result['columns'] = self.adapter.get_model_info(model)['columns']
            
            return jsonify(result)
        
        @bp.route('/api/models/<model_name>', methods=['POST'])
        def api_create_model_data(model_name):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            model = self.adapter.get_model_by_name(model_name)
            if not model:
                return jsonify({'error': 'Model not found'}), 404
            
            data = request.get_json() or {}
            instance = self.crud.create(model, data)
            
            return jsonify({'success': True, 'data': self.crud.model_to_dict(instance, model)}), 201
        
        @bp.route('/api/models/<model_name>/<int:record_id>', methods=['PUT'])
        def api_update_model_data(model_name, record_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            model = self.adapter.get_model_by_name(model_name)
            if not model:
                return jsonify({'error': 'Model not found'}), 404
            
            instance = model.query.get(record_id)
            if not instance:
                return jsonify({'error': 'Record not found'}), 404
            
            data = request.get_json() or {}
            instance = self.crud.update(instance, data)
            
            return jsonify({'success': True, 'data': self.crud.model_to_dict(instance, model)})
        
        @bp.route('/api/models/<model_name>/<int:record_id>', methods=['DELETE'])
        def api_delete_model_data(model_name, record_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            model = self.adapter.get_model_by_name(model_name)
            if not model:
                return jsonify({'error': 'Model not found'}), 404
            
            instance = model.query.get(record_id)
            if not instance:
                return jsonify({'error': 'Record not found'}), 404
            
            self.crud.delete(instance)
            
            return jsonify({'success': True})
        
        @bp.route('/api/monitor/stats', methods=['GET'])
        def api_monitor_stats():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            range_hours = request.args.get('range', 24, type=int)
            stats = self.monitor.get_stats(range_hours=range_hours)
            
            return jsonify(stats)
        
        @bp.route('/api/monitor/logs', methods=['GET'])
        def api_monitor_logs():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            method = request.args.get('method', '')
            status_min = request.args.get('status_min', None, type=int)
            
            logs = self.monitor.get_logs(page=page, per_page=per_page, 
                                         method=method if method else None,
                                         status_min=status_min)
            
            return jsonify(logs)
    
    def _create_default_admin(self, app):
        username = app.config.get('ADMIN_USERNAME', 'admin')
        password = app.config.get('ADMIN_PASSWORD', 'admin123')
        
        existing = self.db.session.query(AdminUser).filter_by(username=username).first()
        if not existing:
            user = AdminUser(
                username=username,
                role='admin',
                is_active=True,
            )
            user.set_password(password)
            self.db.session.add(user)
            self.db.session.commit()
