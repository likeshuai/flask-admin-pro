"""
Flask Admin Pro - Example Application

Usage:
    python app.py
    
Then visit: http://localhost:5000/__admin__/
Default credentials: admin / admin123
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from admin_pro import AdminPro

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['MAIN_APP_DATABASE_URI'] = 'sqlite:///example.db'  # Save for AdminPro restoration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)


# Example models for demonstration
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Post {self.title}>'


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Category {self.name}>'


# Initialize Flask Admin Pro
admin = AdminPro(app, db=db, database_uri='sqlite:///admin.db')


@app.route('/')
def index():
    return """
    <h1>Flask Admin Pro Example</h1>
    <p>Welcome!</p>
    <ul>
        <li><a href="/__admin__/">Admin Dashboard</a></li>
    </ul>
    """


@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return {'users': [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]}


def create_sample_data():
    if User.query.count() == 0:
        users = [
            User(username='alice', email='alice@example.com'),
            User(username='bob', email='bob@example.com'),
        ]
        db.session.add_all(users)
        
        posts = [
            Post(title='Hello World', content='First post!', author_id=1, is_published=True),
            Post(title='Python Tips', content='Python tips...', author_id=1, is_published=True),
        ]
        db.session.add_all(posts)
        
        categories = [
            Category(name='Technology', description='Tech posts'),
            Category(name='Life', description='Daily life'),
        ]
        db.session.add_all(categories)
        
        db.session.commit()
        print("Sample data created!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    print("\n" + "="*50)
    print("Flask Admin Pro Example Application")
    print("="*50)
    print("\n🌐 Application URL: http://localhost:5000/")
    print("🔐 Admin Panel URL: http://localhost:5000/__admin__/")
    print("👤 Default Credentials: admin / admin123")
    print("\nPress Ctrl+C to stop the server.\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
