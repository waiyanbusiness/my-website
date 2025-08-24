import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///elibrary.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "uploads"
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size
    
    # Proxy fix for proper URL generation
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(app.instance_path, app.config["UPLOAD_FOLDER"])
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    with app.app_context():
        # Import models to ensure tables are created
        import models
        db.create_all()
        
        # Create default admin user if none exists
        from models import User
        from werkzeug.security import generate_password_hash
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@elibrary.com',
                full_name='Administrator',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logging.info("Default admin user created: admin/admin123")
        
        # Create default categories
        from models import Category
        if Category.query.count() == 0:
            default_categories = [
                ('Fiction', 'Novels, short stories, and other fictional works'),
                ('Non-Fiction', 'Biographies, memoirs, and factual books'),
                ('Science', 'Scientific research, textbooks, and journals'),
                ('Technology', 'Computer science, programming, and tech guides'),
                ('History', 'Historical accounts, documentaries, and archives'),
                ('Education', 'Textbooks, learning materials, and academic resources'),
                ('Business', 'Management, entrepreneurship, and business guides'),
                ('Literature', 'Classic literature, poetry, and literary criticism')
            ]
            
            for name, description in default_categories:
                category = Category(name=name, description=description)
                db.session.add(category)
            
            db.session.commit()
            logging.info("Default categories created")
    
    return app

# Create app instance
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
