#!/usr/bin/env python3
"""Run Flask Admin Pro. Usage: python run.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# NOTE: Make sure to install dependencies first:
# pip install -r requirements.txt

from app import app, db, create_sample_data

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    print("\n" + "="*50)
    print("Flask Admin Pro")
    print("="*50)
    print("\n🌐 http://localhost:5000/")
    print("🔐 http://localhost:5000/__admin__/")
    print("👤 admin / admin123\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
