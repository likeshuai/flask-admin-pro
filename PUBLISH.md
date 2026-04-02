# PyPI 发布指南

## 📋 发布前准备

### 1. 修改配置信息

编辑以下文件，替换占位符信息：

**pyproject.toml**
```toml
[project]
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

[project.urls]
Homepage = "https://github.com/yourusername/flask-admin-pro"
Repository = "https://github.com/yourusername/flask-admin-pro.git"
```

**src/flask_admin_pro/__init__.py**
```python
__author__ = "Your Name"
__email__ = "your.email@example.com"
```

**.pypirc**
```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # 你的 PyPI API token
```

### 2. 获取 PyPI API Token

1. 访问 https://pypi.org/manage/account/token/
2. 创建新的 API token
3. 复制 token 到 `.pypirc` 文件

### 3. 安装构建工具

```bash
pip install build twine
```

---

## 🚀 发布流程

### 步骤 1: 清理旧文件

```bash
# 删除之前的构建文件
rm -rf build/ dist/ *.egg-info/
rm -rf src/flask_admin_pro.egg-info/
```

### 步骤 2: 运行测试

```bash
# 运行单元测试
pytest tests/

# 检查代码格式
black src/flask_admin_pro/
ruff check src/flask_admin_pro/
```

### 步骤 3: 构建分发包

```bash
# 构建 wheel 和 source distribution
python -m build

# 检查构建结果
ls -la dist/
# 应该看到：
# flask_admin_pro-0.1.0-py3-none-any.whl
# flask_admin_pro-0.1.0.tar.gz
```

### 步骤 4: 检查分发包

```bash
# 使用 twine 检查包
twine check dist/*

# 应该输出：
# PASSED dist/flask_admin_pro-0.1.0-py3-none-any.whl
# PASSED dist/flask_admin_pro-0.1.0.tar.gz
```

### 步骤 5: 发布到 TestPyPI（测试）

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 输入 .pypirc 中配置的 username 和 password
```

### 步骤 6: 测试安装

```bash
# 在虚拟环境中测试
python -m venv test-env
source test-env/bin/activate

# 从 TestPyPI 安装
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple flask-admin-pro

# 测试导入
python -c "import flask_admin_pro; print(flask_admin_pro.__version__)"
```

### 步骤 7: 发布到 PyPI（正式）

```bash
# 确认无误后，上传到 PyPI
twine upload dist/*

# 输入 PyPI 的 username 和 password
```

### 步骤 8: 验证发布

```bash
# 在新环境中安装验证
pip install flask-admin-pro

# 检查版本
pip show flask-admin-pro
```

---

## 📝 版本更新

### 更新版本号

在以下文件中更新版本号：

1. **pyproject.toml**
   ```toml
   [project]
   version = "0.2.0"  # 更新这里
   ```

2. **src/flask_admin_pro/__init__.py**
   ```python
   __version__ = "0.2.0"  # 更新这里
   ```

3. **CHANGELOG.md**
   ```markdown
   ## [0.2.0] - 2026-04-01
   
   ### Added
   - 新功能描述
   
   ### Changed
   - 变更描述
   ```

### 语义化版本规范

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的新功能
- **PATCH**: 向后兼容的问题修复

---

## 🔧 常见问题

### Q: 上传失败 "HTTPError: 400 Bad Request"

**原因**: 包名已存在或元数据有误

**解决**:
```bash
# 检查包名是否已被占用
pip search flask-admin-pro  # (已废弃，使用网页搜索)

# 访问 https://pypi.org/search/?q=flask-admin-pro 检查
```

### Q: 文件大小限制

PyPI 限制：
- 单个文件最大 100MB
- 使用 MANIFEST.in 排除不必要文件

### Q: 如何撤回已发布的版本？

PyPI 不允许删除已发布的版本（安全原因）。只能发布新版本。

---

## 📊 发布后

1. **创建 GitHub Release**
   ```bash
   # 打标签
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```

2. **更新文档**
   - 更新 README.md 中的版本号
   - 更新 CHANGELOG.md

3. **通知用户**
   - 发布博客/推文
   - 更新项目主页

---

## 🛡️ 安全建议

1. **使用 API Token** 而非账号密码
2. **启用双因素认证** (2FA) 在 PyPI 账号
3. **不要提交 .pypirc** 到版本控制
4. **定期轮换 token**

---

## 📚 参考链接

- [PyPI 官方文档](https://pypi.org/help/)
- [打包 Python 项目](https://packaging.python.org/tutorials/packaging-projects/)
- [twine 文档](https://twine.readthedocs.io/)
- [语义化版本](https://semver.org/)
