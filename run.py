#!/usr/bin/env python3
"""Run Flask Admin Pro Professional Edition."""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, create_sample_data

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    print("\n" + "="*60)
    print("🚀 Flask Admin Pro Professional Edition")
    print("="*60)
    print("\n🌐 Application URL: http://localhost:5000/")
    print("🔐 Admin Panel URL: http://localhost:5000/__admin__/")
    print("👤 Default Credentials: admin / admin123")
    print("\n✨ Features:")
    print("   • Modern UI with Element Plus + Vue 3")
    print("   • Automatic CRUD for SQLAlchemy models")  
    print("   • Real-time monitoring and analytics")
    print("   • Multi-theme support with dark mode")
    print("   • Responsive design for all devices")
    print("\nPress Ctrl+C to stop the server.\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
