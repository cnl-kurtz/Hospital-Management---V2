from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --------------------
# 1. CORE AUTHENTICATION
# --------------------
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'doctor', 'patient'
    
    # Relationships (Explicit back_populates)
    # uselist=False ensures One-to-One relationship
    doctor_profile = db.relationship('Doctor', back_populates='user', uselist=False, cascade="all, delete")
    patient_profile = db.relationship('Patient', back_populates='user', uselist=False, cascade="all, delete")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

# --------------------
# 2. PROFILES
# --------------------
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default="bi-hospital") 

    # Relationship: One Department has many Doctors
    doctors = db.relationship('Doctor', back_populates='department_details', lazy=True, cascade="all, delete-orphan")

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # We store the department name string for easy display, 
    # but we also link it to the Department table for integrity
    department_name = db.Column(db.String(100), db.ForeignKey('departments.name'), nullable=True)
    
    full_name = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=True)  # in years
    contact = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(100), nullable=True, default='default.jpg')
    
    is_blacklisted = db.Column(db.Boolean, default=False)
    
    # Availability
    timings = db.Column(db.String(50), default="09:00 AM - 05:00 PM")
    days = db.Column(db.String(50), default="Mon - Fri")
    fee = db.Column(db.Float, default=0.0)

    # Relationships
    user = db.relationship('User', back_populates='doctor_profile', cascade="all, delete")
    department_details = db.relationship('Department', back_populates='doctors')
    appointments = db.relationship('Appointment', back_populates='doctor')

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.String(20), nullable=True) 

    # Relationships
    user = db.relationship('User', back_populates='patient_profile')
    appointments = db.relationship('Appointment', back_populates='patient')

# --------------------
# 3. OPERATIONS
# --------------------
class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    date_str = db.Column(db.String(20), nullable=False) 
    time_slot = db.Column(db.String(20), nullable=False) 
    symptoms = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Scheduled') 
    remarks = db.Column(db.Text, nullable=True)
    
    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    
    # One-to-One with Medical Record
    medical_record = db.relationship('MedicalRecord', back_populates='appointment', uselist=False, cascade="all, delete")

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), unique=True, nullable=False)
    
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=True)
    tests = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    appointment = db.relationship('Appointment', back_populates='medical_record')

