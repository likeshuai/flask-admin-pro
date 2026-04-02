# 数据库配置指南

## 📋 支持的数据库

| 数据库 | 版本 | 推荐场景 |
|--------|------|---------|
| SQLite | 3.x | 开发、测试、小型应用 |
| MySQL | 5.7+/8.0+ | 生产环境 |
| PostgreSQL | 10+ | 生产环境 |
| MariaDB | 10.3+ | 生产环境 |

---

## 🔧 配置方法

### 方法 1: 环境变量（推荐）

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env
vi .env

# 设置数据库 URL
DATABASE_URL=sqlite:///admin.db
# 或
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/dbname
```

### 方法 2: 修改 config.py

```python
# app/config.py
class Config:
    # SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///admin.db'
    
    # MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@localhost:3306/dbname?charset=utf8mb4'
    
    # PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost:5432/dbname'
```

---

## 📦 安装驱动

### SQLite
```bash
# Python 内置，无需安装
pip install flask-sqlalchemy
```

### MySQL
```bash
pip install pymysql cryptography
```

### PostgreSQL
```bash
pip install psycopg2-binary
```

### MariaDB
```bash
pip install mariadb
```

---

## 🚀 快速开始

### SQLite（默认）

```bash
# 无需额外配置
python run.py

# 访问
http://localhost:5001/__admin__/
```

### MySQL

```bash
# 1. 创建数据库
mysql -u root -p
CREATE DATABASE flask_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

# 2. 配置
export DATABASE_URL="mysql+pymysql://root:password@localhost:3306/flask_admin?charset=utf8mb4"

# 3. 初始化
flask init-db
flask init-admin

# 4. 启动
python run.py
```

### PostgreSQL

```bash
# 1. 创建数据库
createdb flask_admin

# 2. 配置
export DATABASE_URL="postgresql://postgres:password@localhost:5432/flask_admin"

# 3. 初始化
flask init-db
flask init-admin

# 4. 启动
python run.py
```

---

## ⚙️ 生产环境配置

### Docker 环境

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:pass@db:5432/flask_admin
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=flask_admin
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 连接池配置

```python
# app/config.py
class Config:
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,          # 连接池大小
        'max_overflow': 20,       # 最大溢出连接数
        'pool_recycle': 300,      # 连接回收时间（秒）
        'pool_pre_ping': True,    # 使用前检查连接
    }
```

---

## 🔍 故障排查

### 问题：无法连接数据库

```bash
# 检查数据库服务
systemctl status mysql
# 或
systemctl status postgresql

# 检查连接
mysql -u user -p -h localhost
# 或
psql -U user -h localhost -d dbname
```

### 问题：编码错误

确保数据库和表使用 UTF-8：

```sql
-- MySQL
ALTER DATABASE dbname CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- PostgreSQL
-- 创建时指定
CREATE DATABASE dbname ENCODING 'UTF8';
```

### 问题：连接超时

增加连接超时配置：

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'connect_args': {
        'connect_timeout': 10
    }
}
```

---

## 📊 数据库迁移

```bash
# 初始化迁移
flask db init

# 创建迁移脚本
flask db migrate -m "Initial migration"

# 应用迁移
flask db upgrade

# 回滚
flask db downgrade
```

---

## 💡 最佳实践

1. **开发环境**: 使用 SQLite，简单快速
2. **生产环境**: 使用 MySQL/PostgreSQL，稳定可靠
3. **密码管理**: 使用环境变量，不要硬编码
4. **连接池**: 生产环境配置连接池，提高性能
5. **备份**: 定期备份数据库
6. **监控**: 监控数据库连接数和性能
