"""
Flask Admin Pro - Main Blueprint and initialization.
"""

import time
import json
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .core.auth import AuthManager
from .core.crud import CRUDManager
from .core.orm_adapter import ORMAdapter
from .core.monitor import MonitorManager

# Initialize extensions
login_manager = LoginManager()
csrf = CSRFProtect()


class AdminPro:
    """Flask Admin Pro main class."""
    
    def __init__(self, app=None, db=None, database_uri=None, **kwargs):
        self.app = app
        self.db = db
        self.database_uri = database_uri
        self.auth = None
        self.crud = None
        self.adapter = None
        self.monitor = None
        
        if app is not None and db is not None:
            self.init_app(app, db, database_uri, **kwargs)
    
    def init_app(self, app, db, database_uri=None, **kwargs):
        self.app = app
        self.db = db
        self.database_uri = database_uri or 'sqlite:///admin.db'
        
        # Configure AdminPro settings
        app.config.setdefault('ADMIN_DATABASE_URI', self.database_uri)
        app.config.setdefault('ADMIN_USERNAME', 'admin')
        app.config.setdefault('ADMIN_PASSWORD', 'admin123')
        app.config.setdefault('ADMIN_ENABLE_MONITOR', True)
        app.config.setdefault('ADMIN_LOG_REQUEST_BODY', True)
        app.config.setdefault('ADMIN_LOG_RESPONSE_BODY', True)
        
        # Create models using the provided db instance
        from .models import create_admin_models
        AdminUser, RequestLog, AuditLog, SystemConfig = create_admin_models(db)
        self.AdminUser = AdminUser
        self.RequestLog = RequestLog
        self.AuditLog = AuditLog
        self.SystemConfig = SystemConfig
        
        login_manager.init_app(app)
        csrf.init_app(app)
        
        self.crud = CRUDManager(db)
        self.adapter = ORMAdapter(db)
        self.monitor = MonitorManager(db, RequestLog)
        self.auth = AuthManager(app, AdminUser)
        
        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(AdminUser, int(user_id))
        
        admin_bp = Blueprint('admin', __name__, 
                            url_prefix='/__admin__',
                            template_folder='templates',
                            static_folder='static')
        
        self._register_routes(admin_bp)
        csrf.exempt(admin_bp)
        
        app.register_blueprint(admin_bp)
        
        # Create tables and default admin
        with app.app_context():
            db.create_all()
            self._create_default_admin(app)
            self._create_default_configs()
        
        if app.config.get('ADMIN_ENABLE_MONITOR', True):
            @app.before_request
            def before_request():
                request.start_time = time.time()
                # Store request body for logging
                if app.config.get('ADMIN_LOG_REQUEST_BODY', True):
                    try:
                        request._admin_body = request.get_data(as_text=True)[:10000]
                    except Exception:
                        request._admin_body = None
            
            @app.after_request
            def after_request(response):
                # Exclude Admin backend requests
                if hasattr(request, 'start_time') and not request.path.startswith('/__admin__'):
                    response_time = (time.time() - request.start_time) * 1000
                    
                    # Get response body if configured
                    response_body = None
                    if app.config.get('ADMIN_LOG_RESPONSE_BODY', True):
                        try:
                            if response.content_type and 'json' in response.content_type:
                                response_body = response.get_data(as_text=True)[:10000]
                        except Exception:
                            pass
                    
                    # Get request headers
                    headers_dict = {}
                    for key, value in request.headers:
                        if key.lower() not in ['cookie', 'authorization']:
                            headers_dict[key] = value
                    
                    self.monitor.log_request(
                        method=request.method,
                        path=request.path,
                        status_code=response.status_code,
                        response_time=response_time,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')[:500],
                        request_headers=json.dumps(headers_dict)[:2000] if headers_dict else None,
                        request_body=getattr(request, '_admin_body', None),
                        response_body=response_body,
                    )
                return response
    
    def _log_audit(self, action, resource_type=None, resource_id=None, old_value=None, new_value=None):
        """Log an audit event."""
        try:
            user = self.auth.get_current_user()
            log = self.AuditLog(
                user_id=user.id if user else None,
                username=user.username if user else 'System',
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                old_value=json.dumps(old_value) if old_value else None,
                new_value=json.dumps(new_value) if new_value else None,
                ip_address=request.remote_addr,
            )
            self.db.session.add(log)
            self.db.session.commit()
        except Exception as e:
            print(f"[AdminPro] Audit log error: {e}")
    
    def _register_routes(self, bp):
        @bp.route('/')
        def index():
            if self.auth.is_authenticated():
                try:
                    users_response = self.db.session.query(self.AdminUser).count()
                    models_response = len(self.adapter.get_models())
                    monitor_response = self.monitor.get_stats(range_hours=24)
                    
                    stats = {
                        'user_count': users_response,
                        'model_count': models_response,
                        'request_count': monitor_response.get('total_requests', 0),
                        'error_rate': monitor_response.get('error_rate', 0)
                    }
                except Exception:
                    stats = {'user_count': 0, 'model_count': 0, 'request_count': 0, 'error_rate': 0}
                
                return render_template('admin/dashboard.html', user=self.auth.get_current_user(), stats=stats)
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
            try:
                stats = self.monitor.get_stats(range_hours=24)
            except Exception:
                stats = {}
            return render_template('admin/monitor.html', user=self.auth.get_current_user(), stats=stats)
        
        @bp.route('/monitor/<int:log_id>')
        def monitor_detail(log_id):
            if not self.auth.is_authenticated():
                return redirect(url_for('admin.login'))
            log = self.db.session.get(self.RequestLog, log_id)
            if not log:
                return redirect(url_for('admin.monitor'))
            return render_template('admin/monitor_detail.html', user=self.auth.get_current_user(), log=log)
        
        @bp.route('/audit-logs')
        def audit_logs():
            if not self.auth.is_authenticated():
                return redirect(url_for('admin.login'))
            return render_template('admin/audit_logs.html', user=self.auth.get_current_user())
        
        @bp.route('/system-config')
        def system_config():
            if not self.auth.is_authenticated():
                return redirect(url_for('admin.login'))
            return render_template('admin/system_config.html', user=self.auth.get_current_user())
        
        # API Routes
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
                self._log_audit('LOGIN', 'User', user.id)
                return jsonify({'success': True, 'user': user.to_dict()})
            
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        @bp.route('/api/logout', methods=['POST'])
        def api_logout():
            user = self.auth.get_current_user()
            if user:
                self._log_audit('LOGOUT', 'User', user.id)
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

            result = self.crud.get_all(self.AdminUser, page=page, per_page=per_page, search=search)
            # Rename 'data' to 'items' for consistency with other APIs
            result['items'] = result.pop('data', [])
            return jsonify(result)
        
        @bp.route('/api/users', methods=['POST'])
        def api_create_user():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json() or {}
            
            if not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Username and password required'}), 400
            
            if self.db.session.query(self.AdminUser).filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already exists'}), 400
            
            user = self.AdminUser(
                username=data['username'],
                email=data.get('email'),
                role=data.get('role', 'admin'),
                is_active=data.get('is_active', True),
            )
            user.set_password(data['password'])
            
            self.db.session.add(user)
            self.db.session.commit()
            
            self._log_audit('CREATE', 'User', user.id, new_value=user.to_dict())
            
            return jsonify({'success': True, 'user': user.to_dict()}), 201
        
        @bp.route('/api/users/<int:user_id>', methods=['PUT'])
        def api_update_user(user_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            user = self.db.session.get(self.AdminUser, user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            old_value = user.to_dict()
            data = request.get_json() or {}
            
            if 'username' in data:
                existing = self.db.session.query(self.AdminUser).filter_by(username=data['username']).first()
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
            
            self._log_audit('UPDATE', 'User', user.id, old_value=old_value, new_value=user.to_dict())
            
            return jsonify({'success': True, 'user': user.to_dict()})
        
        @bp.route('/api/users/<int:user_id>', methods=['DELETE'])
        def api_delete_user(user_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            user = self.db.session.get(self.AdminUser, user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if self.auth.get_current_user().id == user_id:
                return jsonify({'error': 'Cannot delete yourself'}), 400
            
            old_value = user.to_dict()
            self.db.session.delete(user)
            self.db.session.commit()
            
            self._log_audit('DELETE', 'User', user_id, old_value=old_value)
            
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
            model_info = self.adapter.get_model_info(model)
            if model_info:
                result['columns'] = model_info['columns']
            else:
                result['columns'] = []

            # Rename 'data' to 'items' for consistency
            result['items'] = result.pop('data', [])

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
            
            result = self.crud.model_to_dict(instance, model)
            self._log_audit('CREATE', model_name, result.get('id'), new_value=result)
            
            return jsonify({'success': True, 'data': result}), 201
        
        @bp.route('/api/models/<model_name>/<int:record_id>', methods=['PUT'])
        def api_update_model_data(model_name, record_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            model = self.adapter.get_model_by_name(model_name)
            if not model:
                return jsonify({'error': 'Model not found'}), 404
            
            instance = self.db.session.get(model, record_id)
            if not instance:
                return jsonify({'error': 'Record not found'}), 404
            
            old_value = self.crud.model_to_dict(instance, model)
            data = request.get_json() or {}
            instance = self.crud.update(instance, data)
            
            new_value = self.crud.model_to_dict(instance, model)
            self._log_audit('UPDATE', model_name, record_id, old_value=old_value, new_value=new_value)
            
            return jsonify({'success': True, 'data': new_value})
        
        @bp.route('/api/models/<model_name>/<int:record_id>', methods=['DELETE'])
        def api_delete_model_data(model_name, record_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            model = self.adapter.get_model_by_name(model_name)
            if not model:
                return jsonify({'error': 'Model not found'}), 404
            
            instance = self.db.session.get(model, record_id)
            if not instance:
                return jsonify({'error': 'Record not found'}), 404
            
            old_value = self.crud.model_to_dict(instance, model)
            self.crud.delete(instance)
            
            self._log_audit('DELETE', model_name, record_id, old_value=old_value)
            
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
        
        @bp.route('/api/monitor/logs/<int:log_id>', methods=['GET'])
        def api_monitor_log_detail(log_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            log = self.db.session.get(self.RequestLog, log_id)
            if not log:
                return jsonify({'error': 'Log not found'}), 404
            
            return jsonify(log.to_dict())
        
        # Audit Logs API
        @bp.route('/api/audit-logs', methods=['GET'])
        def api_get_audit_logs():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            action = request.args.get('action', '')
            resource_type = request.args.get('resource_type', '')
            
            query = self.db.session.query(self.AuditLog)
            
            if action:
                query = query.filter(self.AuditLog.action == action)
            if resource_type:
                query = query.filter(self.AuditLog.resource_type == resource_type)
            
            total = query.count()
            logs = query.order_by(self.AuditLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
            
            return jsonify({
                'items': [log.to_dict() for log in logs],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page,
            })
        
        # System Config API
        @bp.route('/api/system-config', methods=['GET'])
        def api_get_system_config():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            category = request.args.get('category', '')
            
            query = self.db.session.query(self.SystemConfig)
            if category:
                query = query.filter(self.SystemConfig.category == category)
            
            configs = query.order_by(self.SystemConfig.category, self.SystemConfig.key).all()
            
            return jsonify({
                'items': [c.to_dict() for c in configs],
                'categories': ['general', 'security', 'email', 'api'],
            })
        
        @bp.route('/api/system-config', methods=['POST'])
        def api_create_system_config():
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json() or {}
            
            if not data.get('key'):
                return jsonify({'error': 'Key is required'}), 400
            
            existing = self.db.session.query(self.SystemConfig).filter_by(key=data['key']).first()
            if existing:
                return jsonify({'error': 'Key already exists'}), 400
            
            config = self.SystemConfig(
                key=data['key'],
                value=data.get('value', ''),
                description=data.get('description', ''),
                category=data.get('category', 'general'),
                is_public=data.get('is_public', False),
            )
            
            self.db.session.add(config)
            self.db.session.commit()
            
            self._log_audit('CREATE', 'SystemConfig', config.id, new_value=config.to_dict())
            
            return jsonify({'success': True, 'config': config.to_dict()}), 201
        
        @bp.route('/api/system-config/<int:config_id>', methods=['PUT'])
        def api_update_system_config(config_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            config = self.db.session.get(self.SystemConfig, config_id)
            if not config:
                return jsonify({'error': 'Config not found'}), 404
            
            old_value = config.to_dict()
            data = request.get_json() or {}
            
            if 'value' in data:
                config.value = data['value']
            if 'description' in data:
                config.description = data['description']
            if 'category' in data:
                config.category = data['category']
            if 'is_public' in data:
                config.is_public = data['is_public']
            
            self.db.session.commit()
            
            self._log_audit('UPDATE', 'SystemConfig', config.id, old_value=old_value, new_value=config.to_dict())
            
            return jsonify({'success': True, 'config': config.to_dict()})
        
        @bp.route('/api/system-config/<int:config_id>', methods=['DELETE'])
        def api_delete_system_config(config_id):
            if not self.auth.is_authenticated():
                return jsonify({'error': 'Unauthorized'}), 401
            
            config = self.db.session.get(self.SystemConfig, config_id)
            if not config:
                return jsonify({'error': 'Config not found'}), 404
            
            old_value = config.to_dict()
            self.db.session.delete(config)
            self.db.session.commit()
            
            self._log_audit('DELETE', 'SystemConfig', config_id, old_value=old_value)
            
            return jsonify({'success': True})
    
    def _create_default_admin(self, app):
        username = app.config.get('ADMIN_USERNAME', 'admin')
        password = app.config.get('ADMIN_PASSWORD', 'admin123')
        
        existing = self.db.session.query(self.AdminUser).filter_by(username=username).first()
        if not existing:
            user = self.AdminUser(
                username=username,
                role='admin',
                is_active=True,
            )
            user.set_password(password)
            self.db.session.add(user)
            self.db.session.commit()
    
    def _create_default_configs(self):
        """Create default system configurations."""
        defaults = [
            ('site_name', 'Flask Admin Pro', '站点名称', 'general', True),
            ('site_description', 'Professional Admin Dashboard', '站点描述', 'general', True),
            ('items_per_page', '20', '每页显示数量', 'general', True),
            ('session_timeout', '1440', '会话超时时间(分钟)', 'security', False),
            ('max_login_attempts', '5', '最大登录尝试次数', 'security', False),
            ('enable_audit_log', 'true', '启用操作审计', 'security', False),
            ('smtp_host', '', 'SMTP服务器地址', 'email', False),
            ('smtp_port', '587', 'SMTP端口', 'email', False),
            ('api_rate_limit', '100', 'API速率限制(次/分钟)', 'api', False),
        ]
        
        for key, value, desc, category, is_public in defaults:
            existing = self.db.session.query(self.SystemConfig).filter_by(key=key).first()
            if not existing:
                config = self.SystemConfig(
                    key=key,
                    value=value,
                    description=desc,
                    category=category,
                    is_public=is_public,
                )
                self.db.session.add(config)
        
        self.db.session.commit()
