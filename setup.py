"""
Setup script for flask-admin-pro
Legacy setup.py for compatibility with older pip versions
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flask-admin-pro",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A plug-and-play admin dashboard for Flask applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flask-admin-pro",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/flask-admin-pro/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=3.0.0",
        "Flask-SQLAlchemy>=3.1.1",
        "Flask-Login>=0.6.3",
        "Flask-WTF>=1.2.1",
        "Flask-Migrate>=4.0.5",
        "Werkzeug>=3.0.1",
        "SQLAlchemy>=2.0.23",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
        "peewee": ["peewee>=3.17.0"],
        "tortoise": ["tortoise-orm>=0.20.0"],
    },
)
