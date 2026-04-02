# 集成指南

## 场景 1: 全新项目

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化
flask init-db
flask init-admin
flask register-models

# 4. 启动
python run.py

# 5. 访问 http://localhost:5000/__admin__/
```

## 场景 2: 现有 Flask + SQLAlchemy 项目

### 步骤 1: 复制核心文件

```bash
# 复制核心模块
cp -r flask-admin-pro/app/core your_project/app/
cp -r flask-admin-pro/app/admin your_project/app/
cp -r flask-admin-pro/app/api your_project/app/
```

### 步骤 2: 修改应用工厂

```python
# 在你的 app/__init__.py 中添加

def create_app():
    app = Flask(__name__)
    app.config.from_object('your_app.config.Config')
    
    # 初始化你的扩展
    db.init_app(app)
    login_manager.init_app(app)
    
    # ========== 添加以下代码 ==========
    # 注册管理后台蓝图
    from app.admin.views import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/__admin__')
    
    # 注册模型到 CRUD 系统
    from app.core.registry import registry
    from app.models import User, YourModel  # 你的模型
    registry.register(User, YourModel)
    registry.init_adapter(User, db)
    # ==================================
    
    return app
```

### 步骤 3: 确保用户模型兼容

```python
# 你的 User 模型需要继承 UserMixin

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### 步骤 4: 添加管理员初始化命令

```python
# 在你的 CLI 命令中添加

@app.cli.command('init-admin')
def init_admin():
    from app.models.user import User, Role
    from app import db
    
    with app.app_context():
        # 创建角色
        if not Role.query.filter_by(name='admin').first():
            role = Role(name='admin', permissions={'*': True})
            db.session.add(role)
        
        # 创建管理员
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
        
        db.session.commit()
        print('✓ 管理员账户已创建')
```

### 步骤 5: 运行

```bash
flask init-admin
flask run
```

## 场景 3: 使用其他 ORM (Peewee)

```python
# run.py
from peewee import Model, SqliteDatabase, CharField, BooleanField

db = SqliteDatabase('app.db')

class User(Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    is_admin = BooleanField(default=False)
    
    class Meta:
        database = db

# 注册到 CRUD 系统
from app.core.registry import registry
registry.register(User)
registry.init_adapter(User)  # 自动检测为 Peewee

# 启动
python run.py
```

## 常见问题

### Q: 如何修改管理后台 URI？

```python
# 在注册蓝图时修改
app.register_blueprint(admin_bp, url_prefix='/your-custom-path')
```

### Q: 如何添加自定义模型字段？

```python
# 在你的模型中添加字段即可，CRUD 会自动检测

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    price = db.Column(db.Float)
    description = db.Column(db.Text)  # 自动识别为 textarea
    is_active = db.Column(db.Boolean)  # 自动识别为 checkbox
    created_at = db.Column(db.DateTime)  # 自动识别为 datetime
```

### Q: 如何禁用监控？

```python
# 在 config.py 中设置
class Config:
    MONITOR_ENABLED = False
```

### Q: 如何自定义页面样式？

```html
<!-- 在 app/admin/templates/admin/base.html 中添加 -->
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('admin.static', filename='css/custom.css') }}">
{% endblock %}
```

## 安全加固

### 启用 IP 白名单

```python
# 在 admin/views.py 的 admin_required 装饰器中添加

import socket

ALLOWED_IPS = ['127.0.0.1', '192.168.1.0/24']

def is_ip_allowed(ip):
    # 实现 IP 检查逻辑
    pass

@admin_required
def dashboard():
    if not is_ip_allowed(request.remote_addr):
        abort(403)
```

### 启用双因素认证

```python
# 使用 Flask-Two-Factor-Auth 扩展
pip install flask-two-factor-auth
```

### 配置 HTTPS

```python
# 生产环境配置
class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
```
