# Flask Admin Pro - Vue 前端部署指南

## 快速开始

### 1. 构建 Vue 前端

```bash
cd ui
npm install
npm run build
```

构建完成后，`dist/` 目录包含所有静态资源。

### 2. 集成到 Flask

构建产物已自动输出到 `ui/dist/`，Flask 会自动提供这些静态文件。

### 3. 启动 Flask 应用

```bash
cd ..
python app.py
# 或
flask run
```

访问：http://localhost:5000/admin/

## 生产部署

### 方案 A: Flask 提供静态文件（推荐）

Flask 已经配置好提供 Vue 构建的静态文件，无需额外配置。

```python
# app.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 方案 B: Nginx 提供静态文件

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /admin/static/ {
        alias /path/to/flask-admin-pro/ui/dist/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:5000/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 环境变量

```bash
# .env 文件
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
```

## API 接口说明

所有 API 接口都在 `/admin/api/` 路径下：

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/admin/api/login` | POST | 用户登录 |
| `/admin/api/logout` | POST | 用户登出 |
| `/admin/api/v1/stats` | GET | 获取统计数据 |
| `/admin/api/users` | GET | 获取用户列表 |
| `/admin/api/users` | POST | 创建用户 |
| `/admin/api/users/<id>` | PUT | 更新用户 |
| `/admin/api/users/<id>` | DELETE | 删除用户 |

## 开发模式

开发时启动两个服务：

```bash
# 终端 1 - Flask 后端
cd ~/.openclaw/workspace/flask-admin-pro
flask run --port 5000

# 终端 2 - Vue 前端
cd ~/.openclaw/workspace/flask-admin-pro/ui
npm run dev
```

访问：http://localhost:3000/admin/

Vite 会自动代理 API 请求到 Flask 后端。

## 常见问题

### Q: 构建后访问页面空白
A: 检查浏览器控制台是否有错误，确保 Flask 正确提供了静态文件。

### Q: API 请求 404
A: 确保 Flask 后端 API 路由正确注册，路径为 `/admin/api/xxx`。

### Q: 刷新页面 404
A: Vue Router 使用 History 模式，需要 Flask 提供通配符路由支持。

### Q: 如何修改 API 后端地址
A: 修改 `ui/vite.config.js` 中的 `proxy.target` 配置。

## 性能优化建议

1. **启用 Gzip 压缩**
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

2. **启用 HTTP/2**
   ```nginx
   listen 443 ssl http2;
   ```

3. **静态资源缓存**
   ```nginx
   location /admin/static/ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

4. **使用 CDN**
   将 Element Plus、Vue 等依赖通过 CDN 加载。

## 版本信息

- Vue: 3.5.30
- Element Plus: 2.13.6
- Vite: 8.0.3
- ECharts: 6.0.0
