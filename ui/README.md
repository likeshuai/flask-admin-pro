# Flask Admin Pro - Vue 3 前端

## 技术栈

- **框架**: Vue 3.5+ (Composition API)
- **UI 库**: Element Plus 2.x
- **状态管理**: Pinia
- **路由**: Vue Router 5.x
- **HTTP**: Axios
- **图表**: ECharts 6.x
- **构建工具**: Vite 5.x
- **样式**: SCSS

## 开发指南

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:3000/admin/

### 构建生产版本

```bash
npm run build
```

构建输出目录：`dist/`

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
ui/
├── src/
│   ├── api/              # API 请求模块
│   │   ├── request.js    # Axios 实例配置
│   │   ├── user.js       # 用户相关 API
│   │   └── dashboard.js  # 仪表盘 API
│   ├── layouts/          # 布局组件
│   │   └── MainLayout.vue
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── styles/           # 全局样式
│   │   └── index.scss
│   ├── views/            # 页面组件
│   │   ├── Login.vue
│   │   ├── Dashboard.vue
│   │   ├── Models.vue
│   │   ├── Users.vue
│   │   ├── ApiMonitor.vue
│   │   ├── Logs.vue
│   │   └── Settings.vue
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
└── vite.config.js
```

## API 代理配置

开发环境下，Vite 会代理 `/admin` 请求到 Flask 后端（默认 http://localhost:5000）

修改 `vite.config.js` 中的 `proxy` 配置可调整后端地址。

## 主题定制

修改 `src/styles/index.scss` 中的 CSS 变量可自定义主题。

## 图标使用

所有 Element Plus 图标已全局注册，直接使用：

```vue
<el-icon><User /></el-icon>
<el-icon><Setting /></el-icon>
```

图标列表：https://element-plus.org/zh-CN/component/icon.html

## 注意事项

1. 所有 API 请求会自动添加 `/admin/api` 前缀
2. Token 存储在 `localStorage` 中
3. 路由守卫会自动检查登录状态
4. 生产构建需要部署到 Flask 的静态文件目录
