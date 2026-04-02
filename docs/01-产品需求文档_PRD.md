# Flask Admin Pro - 产品需求文档 (PRD)

**版本**: 1.0  
**创建日期**: 2026-04-02  
**最后更新**: 2026-04-02  
**文档状态**: 正式发布

---

## 1. 文档概述

### 1.1 文档目的

本文档详细描述 Flask Admin Pro 产品的功能需求、非功能需求、用户角色和使用场景，为开发团队、测试团队和利益相关者提供统一的产品理解。

### 1.2 产品定位

Flask Admin Pro 是一个可嵌入现有 Flask 项目的后台管理系统，提供即插即用的管理界面、自动 CRUD 生成、多 ORM 适配和 API 监控功能。

### 1.3 目标用户

- Flask 应用开发者
- 需要快速搭建管理后台的团队
- 需要 API 监控和数据管理功能的企业用户

### 1.4 术语定义

| 术语 | 定义 |
|------|------|
| ORM | 对象关系映射 (Object-Relational Mapping) |
| CRUD | 创建 (Create)、读取 (Read)、更新 (Update)、删除 (Delete) |
| 蓝图 | Flask Blueprint，用于组织相关视图和路由 |
| 中间件 | 在请求处理前后执行的代码 |

---

## 2. 产品概述

### 2.1 产品背景

Flask 是一个轻量级 Python Web 框架，但官方未提供完整的管理后台解决方案。现有的 Flask-Admin 扩展功能有限，不支持多 ORM 适配和现代化前端。Flask Admin Pro 旨在填补这一空白。

### 2.2 产品愿景

成为 Flask 生态中最易用、功能最丰富的管理后台解决方案。

### 2.3 核心价值

1. **即插即用** - 通过特殊 URI (`/__admin__/`) 访问，不影响现有路由
2. **ORM 自适应** - 自动检测 SQLAlchemy/Peewee 等 ORM 框架
3. **自动 CRUD** - 根据模型字段动态生成表单和列表
4. **接口监控** - 自动记录 API 请求日志和性能指标
5. **用户管理** - 内置用户/角色/权限系统
6. **现代化 UI** - Vue 3 + Element Plus，响应式设计

---

## 3. 功能需求

### 3.1 功能模块总览

```
Flask Admin Pro
├── 用户认证模块
│   ├── 登录/登出
│   ├── 会话管理
│   └── 权限控制
├── 数据管理模块
│   ├── 模型扫描与注册
│   ├── CRUD 操作
│   └── 数据导入导出
├── API 监控模块
│   ├── 请求日志
│   ├── 性能统计
│   └── 错误追踪
├── 用户管理模块
│   ├── 用户 CRUD
│   ├── 角色管理
│   └── 操作日志
└── 系统设置模块
    ├── 基础配置
    └── 安全设置
```

### 3.2 用户认证模块

#### 3.2.1 登录功能

| 需求 ID | AUTH-001 |
|---------|----------|
| 需求名称 | 用户登录 |
| 优先级 | P0 - 必须 |
| 功能描述 | 用户可以通过用户名和密码登录管理后台 |
| 输入 | 用户名、密码、记住我选项 |
| 处理逻辑 | 1. 验证用户名和密码<br>2. 检查用户状态（是否激活）<br>3. 创建会话<br>4. 记录登录日志 |
| 输出 | 登录成功跳转首页，失败显示错误提示 |
| 异常处理 | 用户名不存在、密码错误、账户被禁用时显示相应提示 |

#### 3.2.2 登出功能

| 需求 ID | AUTH-002 |
|---------|----------|
| 需求名称 | 用户登出 |
| 优先级 | P0 - 必须 |
| 功能描述 | 用户可以安全登出管理后台 |
| 处理逻辑 | 1. 销毁会话<br>2. 记录登出日志<br>3. 跳转登录页 |

#### 3.2.3 权限控制

| 需求 ID | AUTH-003 |
|---------|----------|
| 需求名称 | 管理员权限控制 |
| 优先级 | P0 - 必须 |
| 功能描述 | 区分普通用户和管理员，限制敏感操作 |
| 权限级别 | - 普通用户：查看数据<br>- 管理员：增删改查、用户管理、系统设置 |

### 3.3 数据管理模块

#### 3.3.1 模型自动扫描

| 需求 ID | DATA-001 |
|---------|----------|
| 需求名称 | 模型自动扫描与注册 |
| 优先级 | P0 - 必须 |
| 功能描述 | 自动扫描 Flask 应用中定义的 SQLAlchemy 模型并注册到管理后台 |
| 处理逻辑 | 1. 扫描 app.models 模块<br>2. 检测类的 __tablename__ 和 metadata 属性<br>3. 注册符合条件的模型<br>4. 初始化 ORM 适配器 |
| 输出 | 注册成功的模型列表 |

#### 3.3.2 ORM 自适应

| 需求 ID | DATA-002 |
|---------|----------|
| 需求名称 | 多 ORM 框架支持 |
| 优先级 | P1 - 重要 |
| 支持的 ORM | - SQLAlchemy（完全支持）<br>- Peewee（支持）<br>- Tortoise ORM（部分支持） |
| 检测机制 | 通过模型属性自动识别 ORM 类型 |

#### 3.3.3 CRUD 操作

| 需求 ID | DATA-003 |
|---------|----------|
| 需求名称 | 动态 CRUD 生成 |
| 优先级 | P0 - 必须 |
| 功能描述 | 根据模型字段自动生成列表、创建、编辑、删除界面 |
| 字段类型映射 | - Integer → 数字输入<br>- String → 文本输入<br>- Text → 文本域<br>- Boolean → 开关<br>- DateTime → 日期时间选择器<br>- Float → 数字输入<br>- JSON → JSON 编辑器 |
| 特殊字段处理 | - email 字段：邮箱格式验证<br>- password 字段：密码加密存储 |

#### 3.3.4 分页与排序

| 需求 ID | DATA-004 |
|---------|----------|
| 需求名称 | 列表分页与排序 |
| 优先级 | P1 - 重要 |
| 功能描述 | 支持分页浏览和按字段排序 |
| 默认配置 | 每页 20 条记录，可按任意字段升序/降序排列 |

### 3.4 API 监控模块

#### 3.4.1 请求日志记录

| 需求 ID | MON-001 |
|---------|----------|
| 需求名称 | API 请求日志记录 |
| 优先级 | P1 - 重要 |
| 记录内容 | - 请求 ID<br>- HTTP 方法<br>- 请求路径<br>- 状态码<br>- 响应时间<br>- 客户端 IP<br>- User-Agent<br>- 请求/响应体（可选） |
| 存储方式 | 数据库表 api_logs |

#### 3.4.2 统计仪表盘

| 需求 ID | MON-002 |
|---------|----------|
| 需求名称 | API 监控统计 |
| 优先级 | P1 - 重要 |
| 统计指标 | - 总请求数<br>- 平均响应时间<br>- 错误请求数<br>- 错误率<br>- 小时级请求趋势 |
| 展示形式 | 数字卡片 + ECharts 折线图 |

#### 3.4.3 日志查询

| 需求 ID | MON-003 |
|---------|----------|
| 需求名称 | 日志查询与详情 |
| 优先级 | P2 - 可选 |
| 功能描述 | 支持分页查看日志列表，点击查看详情 |
| 筛选条件 | 时间范围、状态码、请求方法 |

### 3.5 用户管理模块

#### 3.5.1 用户 CRUD

| 需求 ID | USER-001 |
|---------|----------|
| 需求名称 | 用户管理 |
| 优先级 | P0 - 必须 |
| 功能描述 | 管理员可以创建、查看、编辑、删除用户 |
| 用户字段 | - 用户名（唯一）<br>- 邮箱（唯一）<br>- 密码（加密）<br>- 是否激活<br>- 是否管理员<br>- 角色 |

#### 3.5.2 角色管理

| 需求 ID | USER-002 |
|---------|----------|
| 需求名称 | 角色与权限 |
| 优先级 | P2 - 可选 |
| 功能描述 | 定义角色并分配权限，用户关联角色 |
| 权限类型 | JSON 格式存储，支持自定义权限 |

#### 3.5.3 操作日志

| 需求 ID | USER-003 |
|---------|----------|
| 需求名称 | 操作日志记录 |
| 优先级 | P1 - 重要 |
| 记录内容 | - 操作用户<br>- 操作类型（create/update/delete/login）<br>- 操作模块<br>- 目标对象<br>- 操作详情<br>- IP 地址<br>- 操作状态 |

---

## 4. 非功能需求

### 4.1 性能需求

| 指标 | 要求 |
|------|------|
| 页面加载时间 | < 2 秒（首屏） |
| API 响应时间 | < 500ms（P95） |
| 并发用户数 | 支持 100+ 并发 |
| 数据库查询 | 使用索引，避免 N+1 查询 |

### 4.2 安全需求

| 需求 | 实现方式 |
|------|----------|
| 密码加密 | Werkzeug generate_password_hash |
| CSRF 保护 | Flask-WTF CSRF Token |
| 会话安全 | HttpOnly Cookie，生产环境 Secure |
| SQL 注入防护 | ORM 参数化查询 |
| XSS 防护 | 模板自动转义 |

### 4.3 可用性需求

- 支持 Python 3.8+
- 支持主流浏览器（Chrome、Firefox、Safari、Edge）
- 响应式设计，支持移动端
- 提供完整的错误提示

### 4.4 可维护性需求

- 模块化代码结构
- 完整的单元测试
- 详细的文档
- 清晰的日志输出

### 4.5 兼容性需求

| 组件 | 版本要求 |
|------|----------|
| Python | 3.8+ |
| Flask | 3.0+ |
| SQLAlchemy | 2.0+ |
| Vue | 3.5+ |
| Element Plus | 2.x |

---

## 5. 用户界面需求

### 5.1 设计风格

- **设计语言**: Element Plus 默认主题
- **配色方案**: 蓝色为主色调
- **布局**: 侧边栏导航 + 顶部栏 + 内容区

### 5.2 页面列表

| 页面 | 路径 | 功能 |
|------|------|------|
| 登录页 | /__admin__/login | 用户登录 |
| 仪表盘 | /__admin__/ | 统计概览 |
| 模型列表 | /__admin__/models | 查看所有注册模型 |
| CRUD 页 | /__admin__/models/<name> | 数据管理 |
| API 监控 | /__admin__/monitor | 接口监控 |
| 用户管理 | /__admin__/users | 用户 CRUD |
| 操作日志 | /__admin__/logs | 操作记录 |
| 系统设置 | /__admin__/settings | 配置管理 |

### 5.3 响应式要求

- 桌面端：≥1200px，三栏布局
- 平板端：768px-1199px，侧边栏可折叠
- 移动端：<768px，侧边栏隐藏，汉堡菜单

---

## 6. 数据需求

### 6.1 数据模型

#### 6.1.1 用户表 (users)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| username | String(64) | Unique, Not Null | 用户名 |
| email | String(120) | Unique, Not Null | 邮箱 |
| password_hash | String(256) | Not Null | 密码哈希 |
| is_active | Boolean | Default True | 是否激活 |
| is_admin | Boolean | Default False | 是否管理员 |
| role_id | Integer | FK | 角色 ID |
| created_at | DateTime | Default Now | 创建时间 |
| last_login | DateTime | Nullable | 最后登录 |

#### 6.1.2 角色表 (roles)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| name | String(64) | Unique, Not Null | 角色名 |
| permissions | JSON | Nullable | 权限配置 |
| description | String(256) | Nullable | 描述 |
| created_at | DateTime | Default Now | 创建时间 |

#### 6.1.3 操作日志表 (operation_logs)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| user_id | Integer | FK | 用户 ID |
| username | String(64) | Not Null | 用户名 |
| action | String(50) | Not Null | 操作类型 |
| module | String(50) | Not Null | 模块 |
| target_id | Integer | Nullable | 目标 ID |
| target_type | String(50) | Nullable | 目标类型 |
| details | Text | Nullable | 详情 |
| ip | String(45) | Nullable | IP 地址 |
| status | String(20) | Not Null | 状态 |
| created_at | DateTime | Default Now, Index | 创建时间 |

#### 6.1.4 API 日志表 (api_logs)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| request_id | String(64) | Index | 请求 ID |
| method | String(10) | Not Null | HTTP 方法 |
| endpoint | String(128) | Not Null | 端点 |
| path | String(256) | Not Null | 路径 |
| status_code | Integer | Not Null | 状态码 |
| duration_ms | Float | Not Null | 耗时 (ms) |
| error | Text | Nullable | 错误信息 |
| ip | String(45) | Nullable | IP 地址 |
| user_agent | String(512) | Nullable | User-Agent |
| query_params | Text | Nullable | 查询参数 |
| request_body | Text | Nullable | 请求体 |
| response_body | Text | Nullable | 响应体 |
| created_at | DateTime | Default Now, Index | 创建时间 |

### 6.2 数据保留策略

| 数据类型 | 保留期限 | 清理策略 |
|----------|----------|----------|
| API 日志 | 30 天 | 自动清理过期数据 |
| 操作日志 | 永久 | 手动清理 |
| 用户数据 | 永久 | 软删除（预留） |

---

## 7. 接口需求

### 7.1 RESTful API 规范

#### 7.1.1 通用响应格式

**成功响应**:
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误信息",
  "code": "ERROR_CODE"
}
```

**列表响应**:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "pages": 5,
  "per_page": 20
}
```

### 7.2 API 端点列表

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| POST | /__admin__/api/login | 登录 | 公开 |
| POST | /__admin__/api/logout | 登出 | 已登录 |
| GET | /__admin__/api/models | 获取模型列表 | 已登录 |
| GET | /__admin__/api/models/<name> | 获取模型结构 | 已登录 |
| GET | /__admin__/api/models/<name>/list | 列表查询 | 已登录 |
| POST | /__admin__/api/models/<name>/create | 创建记录 | 已登录 |
| PUT | /__admin__/api/models/<name>/update/<id> | 更新记录 | 已登录 |
| DELETE | /__admin__/api/models/<name>/delete/<id> | 删除记录 | 已登录 |
| GET | /__admin__/api/monitor/stats | 监控统计 | 已登录 |
| GET | /__admin__/api/monitor/logs | 监控日志 | 已登录 |
| GET | /__admin__/api/users | 用户列表 | 管理员 |
| POST | /__admin__/api/users/create | 创建用户 | 管理员 |
| PUT | /__admin__/api/users/<id> | 更新用户 | 管理员 |
| DELETE | /__admin__/api/users/<id> | 删除用户 | 管理员 |

---

## 8. 部署需求

### 8.1 环境要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| Python | 3.8 | 3.11+ |
| 内存 | 512MB | 2GB+ |
| 存储 | 100MB | 1GB+ |
| 数据库 | SQLite | MySQL/PostgreSQL |

### 8.2 部署方式

1. **pip 安装**: `pip install flask-admin-pro`
2. **源码安装**: `pip install -e .`
3. **Docker 部署**: 使用 docker-compose.yml

### 8.3 配置管理

- 使用环境变量管理敏感配置
- 提供 .env.example 模板
- 支持多环境配置（开发/生产）

---

## 9. 验收标准

### 9.1 功能验收

- [ ] 用户可以成功登录/登出
- [ ] 管理员可以管理用户
- [ ] 模型可以自动扫描并注册
- [ ] CRUD 操作可以正常执行
- [ ] API 请求被正确记录
- [ ] 统计图表正确显示

### 9.2 性能验收

- [ ] 首屏加载时间 < 2 秒
- [ ] API 响应时间 < 500ms
- [ ] 支持 100+ 并发用户

### 9.3 安全验收

- [ ] 密码加密存储
- [ ] CSRF 保护生效
- [ ] 会话安全配置正确
- [ ] SQL 注入测试通过

---

## 10. 附录

### 10.1 参考资料

- Flask 官方文档：https://flask.palletsprojects.com/
- SQLAlchemy 文档：https://docs.sqlalchemy.org/
- Vue 3 文档：https://vuejs.org/
- Element Plus 文档：https://element-plus.org/

### 10.2 修订历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| 1.0 | 2026-04-02 | 小李 | 初始版本 |

---

**文档结束**
