# Flask Admin Pro - PyPI 发布快速指南

## 📦 项目已准备好发布到 PyPI

项目结构已完成，包含：
- ✅ `pyproject.toml` - 现代 Python 包配置
- ✅ `setup.py` - 兼容旧版 pip
- ✅ `MANIFEST.in` - 包含模板和静态文件
- ✅ `src/flask_admin_pro/` - 包源码目录
- ✅ `tests/` - 单元测试
- ✅ `LICENSE` - MIT 许可证
- ✅ `.pypirc` - PyPI 配置模板

---

## 🚀 发布步骤

### 1. 安装构建工具

```bash
# 使用 pip3 或 python -m pip
pip3 install build twine
# 或
python3 -m pip install build twine
```

### 2. 修改配置信息

编辑以下文件，替换为你的信息：

**pyproject.toml** (第 8-10 行):
```toml
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

[project.urls]
Homepage = "https://github.com/yourusername/flask-admin-pro"
```

**src/flask_admin_pro/__init__.py** (第 19-21 行):
```python
__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
```

**.pypirc**:
```ini
[pypi]
username = __token__
password = pypi-你的 PyPI API token
```

### 3. 获取 PyPI API Token

1. 访问 https://pypi.org/manage/account/token/
2. 创建新的 API token
3. 复制 token 到 `.pypirc` 文件

### 4. 构建分发包

```bash
cd /home/admin/.openclaw/workspace/flask-admin-pro

# 清理旧文件
rm -rf build/ dist/ *.egg-info/ src/*.egg-info/

# 构建
python3 -m build
```

构建成功后会在 `dist/` 目录生成：
- `flask_admin_pro-0.1.0-py3-none-any.whl`
- `flask_admin_pro-0.1.0.tar.gz`

### 5. 检查分发包

```bash
python3 -m twine check dist/*
```

应该输出：`PASSED`

### 6. 发布到 TestPyPI（测试）

```bash
python3 -m twine upload --repository testpypi dist/*
```

### 7. 测试安装

```bash
# 创建测试虚拟环境
python3 -m venv /tmp/test-env
source /tmp/test-env/bin/activate

# 从 TestPyPI 安装
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    flask-admin-pro

# 测试导入
python -c "import flask_admin_pro; print(flask_admin_pro.__version__)"
```

### 8. 发布到 PyPI（正式）

```bash
python3 -m twine upload dist/*
```

---

## 📝 版本更新流程

### 更新版本号

1. **pyproject.toml**: `version = "0.2.0"`
2. **src/flask_admin_pro/__init__.py**: `__version__ = "0.2.0"`
3. **CHANGELOG.md**: 添加新版本记录

### 重新发布

```bash
# 清理
rm -rf build/ dist/

# 构建
python3 -m build

# 上传
python3 -m twine upload dist/*
```

---

## 🛠️ 常用命令

```bash
# 本地安装测试
pip install -e .

# 运行测试
pip install pytest
pytest tests/

# 检查代码格式
pip install black ruff
black src/flask_admin_pro/
ruff check src/flask_admin_pro/

# 查看包信息
python3 -m pip show flask-admin-pro

# 列出包内容
python3 -m zipinfo dist/flask_admin_pro-0.1.0-py3-none-any.whl
```

---

## ⚠️ 注意事项

1. **包名唯一性**: 确保 `flask-admin-pro` 在 PyPI 上未被占用
   - 检查：https://pypi.org/search/?q=flask-admin-pro

2. **不要重复版本**: PyPI 不允许删除已发布的版本
   - 每次发布使用新版本号

3. **文件大小**: 单个文件不超过 100MB

4. **安全**: 
   - 使用 API token 而非密码
   - 启用 PyPI 双因素认证
   - 不要提交 `.pypirc` 到 Git

---

## 📚 参考资源

- [PyPI 官方文档](https://pypi.org/help/)
- [Python 打包指南](https://packaging.python.org/)
- [twine 文档](https://twine.readthedocs.io/)

---

## 🎯 下一步

1. 修改配置中的占位符信息
2. 获取 PyPI API token
3. 运行构建命令
4. 发布到 TestPyPI 测试
5. 正式发布到 PyPI
6. 创建 GitHub Release

祝发布顺利！🎉
