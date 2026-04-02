# Flask Admin Pro

> 基于 Vue 3 + Element Plus 的现代化 Flask 管理后台

## ✨ 特性

- 🎨 **现代化 UI** - 采用 Vue 3 + Element Plus，设计美观、交互流畅
- 🚀 **快速开发** - 开箱即用的管理后台模板
- 🔒 **安全可靠** - 完善的权限控制和操作审计
- 📊 **数据可视** - ECharts 图表支持，数据一目了然
- 📱 **响应式** - 完美支持桌面和移动端
- 🌙 **暗黑模式** - 内置暗黑模式支持
- 🔧 **易扩展** - 模块化设计，易于二次开发

## 🛠️ 技术栈

### 前端
- **框架**: Vue 3.5+ (Composition API)
- **UI 库**: Element Plus 2.x
- **状态管理**: Pinia
- **路由**: Vue Router 5.x
- **HTTP**: Axios
- **图表**: ECharts 6.x
- **构建工具**: Vite 5.x

### 后端
- **框架**: Flask 3.x
- **ORM**: SQLAlchemy
- **认证**: Flask-Login
- **数据库**: SQLite / PostgreSQL

## 📦 安装

### 1. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd ui
npm install
```

### 2. 构建前端

```bash
cd ui
npm run build
```

### 3. 启动应用

```bash
# 方式一：直接运行
python app.py

# 方式二：Flask 命令
export FLASK_APP=app.py
flask run
```

访问：http://localhost:5000/admin/

## 📁 项目结构

```
flask-admin-pro/
├── app/                      # Flask 应用
│   ├── admin/               # 管理后台视图
│   ├── core/                # 核心模块
│   ├── models/              # 数据模型
│   ├── templates/           # HTML 模板
│   └── vue_views.py         # Vue 前端视图
├── ui/                      # Vue 前端
│   ├── src/
│   │   ├── api/            # API 请求
│   │   ├── layouts/        # 布局组件
│   │   ├── router/         # 路由配置
│   │   ├── styles/         # 样式文件
│   │   └── views/          # 页面组件
│   ├── dist/               # 构建输出
│   └── package.json
├── requirements.txt         # Python 依赖
├── DEPLOYMENT.md           # 部署文档
└── README.md               # 说明文档
```

## 🎯 功能模块

| 模块 | 状态 | 说明 |
|-----|------|------|
| 仪表盘 | ✅ | 数据统计、趋势图表 |
| 数据模型 | ✅ | CRUD 操作、数据管理 |
| 用户管理 | ✅ | 用户 CRUD、权限控制 |
| API 监控 | 🚧 | 接口监控、性能分析 |
| 操作日志 | 🚧 | 操作审计、日志查询 |
| 系统设置 | 🚧 | 系统配置管理 |

✅ 已完成  🚧 开发中

## 🔐 默认账号

- 用户名：`admin`
- 密码：`admin123`

**⚠️ 首次使用后请立即修改密码！**

## 📖 开发指南

### 开发模式

启动两个服务：

```bash
# 终端 1 - Flask 后端 (端口 5000)
flask run --port 5000

# 终端 2 - Vue 前端 (端口 3000)
cd ui
npm run dev
```

访问：http://localhost:3000/admin/

### 添加新页面

1. 在 `ui/src/views/` 创建新组件
2. 在 `ui/src/router/index.js` 添加路由
3. 在 `ui/src/layouts/MainLayout.vue` 添加菜单项

### 添加 API 接口

1. 在 `ui/src/api/` 创建 API 模块
2. 在 Flask 后端添加对应路由
3. 确保 API 路径以 `/admin/api/` 开头

## 📝 更新日志

### v2.0.0 (2026-04-02)
- ✨ 重构前端为 Vue 3 + Element Plus
- ✨ 新增现代化仪表盘
- ✨ 支持暗黑模式
- 🐛 修复统计数据显示问题
- 🐛 修复时间范围切换问题

### v1.0.0 (2026-03-01)
- ✨ 初始版本
- ✨ Bootstrap 5 前端
- ✨ 基础 CRUD 功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 联系方式

- Email: admin@example.com
- GitHub: [项目地址]

---

**Made with ❤️ using Vue 3 + Element Plus**
