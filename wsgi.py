from app import app, db
import os

def init_db():
    with app.app_context():
        try:
            # Ensure the instance folder exists
            instance_path = os.path.join(app.root_path, 'instance')
            os.makedirs(instance_path, exist_ok=True)
            
            # Create database file if it doesn't exist
            db_path = os.path.join(instance_path, 'site.db')
            if not os.path.exists(db_path):
                open(db_path, 'a').close()
                print(f"Created empty database at {db_path}")
            
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Create a test user if none exists
            from models import User
            if not User.query.filter_by(email='test@example.com').first():
                user = User(username='test', email='test@example.com')
                user.set_password('test123')
                db.session.add(user)
                db.session.commit()
                print("Created test user")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

# Initialize the database
init_db()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
