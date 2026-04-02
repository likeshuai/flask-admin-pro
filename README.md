# Flask Admin Pro

🤖 一个可嵌入 Flask 项目的后台管理系统，零前端构建成本，开箱即用！

## ✨ 特性

- 🔌 **即插即用** - 一行代码集成到现有 Flask 项目
- 📦 **零构建** - 无需 Node.js，无需 npm，无需 webpack/vite
- 🎨 **现代化 UI** - Element Plus + Vue 3，通过 CDN 引入
- 🔒 **安全可靠** - 内置认证、权限、日志监控
- 📊 **自动 CRUD** - 自动扫描 SQLAlchemy 模型生成管理界面
- 🌙 **主题系统** - 5 种主题色 + 黑夜模式

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行示例项目

```bash
cd flask-admin-pro
python run.py
```

访问：
- 应用首页：http://localhost:5000/
- 管理后台：http://localhost:5000/__admin__/
- 默认账号：`admin` / `admin123`

## 📖 功能模块

### 认证系统
- ✅ 登录/登出
- ✅ 会话管理
- ✅ 权限验证

### 用户管理
- ✅ 用户列表（分页、搜索）
- ✅ 新增/编辑/删除用户
- ✅ 角色管理（admin/operator）
- ✅ 启用/禁用用户

### 模型管理
- ✅ 自动扫描 SQLAlchemy 模型
- ✅ 列表展示（分页、排序、搜索）
- ✅ 新增/编辑/删除记录
- ✅ 支持多种字段类型

### 监控中心
- ✅ API 请求统计
- ✅ 请求日志列表
- ✅ 错误请求追踪
- ✅ 响应时间统计

### 界面主题
- ✅ 5 种主题色（蓝/紫/绿/橙/红）
- ✅ 黑夜模式
- ✅ localStorage 持久化
- ✅ 响应式布局

## 📁 项目结构

```
flask-admin-pro/
├── docs/                          # 文档
│   ├── 01-产品设计文档.md
│   ├── 02-需求开发文档.md
│   └── 03-产品需求文档.md
├── app/
│   ├── app.py                     # 主应用入口
│   ├── admin_pro/                 # Admin Pro 核心模块
│   │   ├── __init__.py
│   │   ├── admin.py               # 主入口
│   │   ├── models.py              # 数据模型
│   │   ├── extensions.py          # 扩展初始化
│   │   ├── core/                  # 核心模块
│   │   │   ├── auth.py           # 认证
│   │   │   ├── crud.py           # CRUD
│   │   │   ├── orm_adapter.py    # ORM 适配
│   │   │   └── monitor.py        # 监控
│   │   ├── templates/admin/       # 前端模板
│   │   └── static/admin/          # 静态资源
│   └── ...
├── run.py                         # 运行脚本
├── requirements.txt
└── README.md
```

## 💡 集成到你的项目

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from admin_pro import AdminPro

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)

# 定义你的模型
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 初始化 Admin Pro
admin = AdminPro(app, database_uri='sqlite:///admin.db')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

## ⚙️ 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `ADMIN_DATABASE_URI` | `sqlite:///admin.db` | 管理后台数据库 |
| `ADMIN_USERNAME` | `admin` | 默认管理员用户名 |
| `ADMIN_PASSWORD` | `admin123` | 默认管理员密码 |
| `ADMIN_ENABLE_MONITOR` | `True` | 启用请求监控 |

## 📝 文档

- [产品设计文档](docs/01-产品设计文档.md)
- [需求开发文档](docs/02-需求开发文档.md)
- [产品需求文档](docs/03-产品需求文档.md)

---

**Made with ❤️ for Flask developers**
