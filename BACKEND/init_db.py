from flask import Flask
from flask_bcrypt import Bcrypt
from models import db, User, Department
import os

app = Flask(__name__)

# --- CONFIG ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

def init_database():
    with app.app_context():
        # 1. Wipe and Recreate Tables (Optional: remove db.drop_all() if you want to keep data later)
        # db.drop_all() 
        db.create_all()
        print(f">>> Database connected at: {os.path.join(basedir, 'hospital.db')}")

        # 2. Create Admin
        admin_email = "admin@hplus.com"
        existing_admin = User.query.filter_by(email=admin_email).first()

        if not existing_admin:
            hashed_pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
            new_admin = User(
                username="admin",
                email=admin_email,
                password_hash=hashed_pw,
                role="admin"
                # Admin does not need a Patient or Doctor profile entry
            )
            db.session.add(new_admin)
            print(f">>> Admin created: {admin_email} | Pass: admin123")
        else:
            print(">>> Admin already exists.")

        # 3. Create Default Departments (So the frontend dropdowns work)
        default_depts = [
            {"name": "Cardiology", "desc": "Heart & Vascular care", "icon": "bi-heart-pulse"},
            {"name": "Neurology", "desc": "Brain & Nervous system", "icon": "bi-activity"},
            {"name": "Pediatrics", "desc": "Child healthcare", "icon": "bi-emoji-smile"},
            {"name": "Orthopedics", "desc": "Bone & Joint care", "icon": "bi-person-walking"},
            {"name": "General Surgery", "desc": "General surgical procedures", "icon": "bi-hospital"}
        ]

        for dept_data in default_depts:
            exists = Department.query.filter_by(name=dept_data["name"]).first()
            if not exists:
                new_dept = Department(
                    name=dept_data["name"],
                    description=dept_data["desc"],
                    icon=dept_data["icon"]
                )
                db.session.add(new_dept)
        
        db.session.commit()
        print(">>> Default Departments seeded.")

if __name__ == "__main__":
    init_database()