from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os

# Import Models
from models import db, User, Doctor, Patient, Department, Appointment, MedicalRecord

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this' # Change for production!

# Extensions
CORS(app) 
db.init_app(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

# --- HELPER: CHECK WORKING DAYS ---
def is_working_day(date_obj, days_str):
    """
    Checks if date_obj falls within the doctor's working schedule.
    Supports: "Mon - Fri", "Fri - Mon" (wrap-around), "Mon, Wed, Fri"
    """
    if not days_str: return True # Default to working if undefined
    
    # 1. Standardize Input
    # Remove dots/spaces, ensure strict "Mon", "Tue" format
    days_str = days_str.replace('.', '').strip()
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # 2. Get Target Day (e.g., "Sun")
    target_day = date_obj.strftime('%a') 
    
    # CASE A: Comma Separated List (e.g., "Mon, Wed, Fri")
    if ',' in days_str:
        allowed_days = [d.strip()[:3] for d in days_str.split(',')]
        return target_day in allowed_days

    # CASE B: Range (e.g., "Mon - Fri" OR "Fri - Mon")
    elif '-' in days_str:
        try:
            start_str, end_str = [d.strip()[:3] for d in days_str.split('-')]
            
            # Get indices (0=Mon, 6=Sun)
            s_idx = week_days.index(start_str)
            e_idx = week_days.index(end_str)
            t_idx = week_days.index(target_day)
            
            # Logic: Standard Range vs Wrap-Around
            if s_idx <= e_idx:
                return s_idx <= t_idx <= e_idx
            else:
                # Wrap-around (e.g., Fri(4) to Mon(0))
                # Valid if index is >= 4 (Fri, Sat, Sun) OR <= 0 (Mon)
                return t_idx >= s_idx or t_idx <= e_idx
        except ValueError:
            return True # Fallback if format is weird (e.g. typos)
            
    # CASE C: Single Day (e.g., "Mon")
    return target_day == days_str[:3]


def generate_slots(start_str, end_str):
    """ Generates 30-min slots between start and end time strings (e.g., '09:00 AM') """
    slots = []
    try:
        fmt = "%I:%M %p"
        current = datetime.strptime(start_str, fmt)
        end = datetime.strptime(end_str, fmt)
        
        while current < end:
            slots.append(current.strftime(fmt))
            current += timedelta(minutes=30)
    except Exception as e:
        print(f"Error generating slots: {e}")
        return [] 
    return slots

@app.route('/')
def home():
    return "H+ HealthCare API is Running with Organized Schema!"

# ==========================================
# 1. AUTHENTICATION (Login & Register)
# ==========================================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('email') 
    password = data.get('password')

    user = User.query.filter(or_(User.email == identifier, User.username == identifier)).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        
        real_name = user.username 
        doc_id = None
        pat_id = None

        if user.role == 'patient' and user.patient_profile:
            real_name = user.patient_profile.full_name
            pat_id = user.patient_profile.id
        elif user.role == 'doctor' and user.doctor_profile:
            real_name = user.doctor_profile.full_name
            doc_id = user.doctor_profile.id
        elif user.role == 'admin':
            real_name = "Administrator"

        access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
        
        return jsonify({
            "message": "Login successful",
            "token": access_token,
            "role": user.role,
            "username": user.username,
            "name": real_name,
            "id": user.id,
            "doctor_id": doc_id,
            "patient_id": pat_id
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register_patient():
    data = request.get_json()
    required_fields = ['name', 'username', 'email', 'password', 'dob', 'phone']
    for field in required_fields:
        if not data.get(field): return jsonify({"error": f"{field} is required"}), 400

    if User.query.filter((User.email == data['email']) | (User.username == data['username'])).first():
        return jsonify({"error": "User already exists"}), 400
    
    try:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], email=data['email'], password_hash=hashed_pw, role='patient')
        db.session.add(new_user)
        db.session.flush() 

        new_patient = Patient(user_id=new_user.id, full_name=data['name'], phone=data.get('phone'), dob=data.get('dob'))
        db.session.add(new_patient)
        db.session.commit()
        return jsonify({"message": "Patient registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500

# ==========================================
# 2. ADMIN ROUTES
# ==========================================

# --- GLOBAL ADMIN SEARCH ---
@app.route('/api/admin/global_search', methods=['GET'])
@jwt_required()
def admin_global_search():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({}) # Return empty if query is too short

    search_term = f"%{query}%"
    
    # 1. Search Doctors (Name or Department)
    doctors = Doctor.query.filter(
        (Doctor.full_name.ilike(search_term)) | 
        (Doctor.department_name.ilike(search_term))
    ).all()
    
    # 2. Search Departments
    depts = Department.query.filter(Department.name.ilike(search_term)).all()
    
    # 3. Search Patients (Only those with appointments)
    # We join Appointment to ensure they have history
    patients = db.session.query(Patient).join(Appointment).filter(
        Patient.full_name.ilike(search_term)
    ).distinct().all()

    return jsonify({
        "doctors": [{"id": d.id, "name": d.full_name, "dept": d.department_name} for d in doctors],
        "departments": [{"id": d.id, "name": d.name} for d in depts],
        "patients": [{"id": p.id, "name": p.full_name} for p in patients]
    }), 200

# --- ADD DOCTOR ---
@app.route('/api/admin/add_doctor', methods=['POST'])
@jwt_required()
def add_doctor():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first(): 
        return jsonify({"error": "Email already registered"}), 400

    try:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], email=data['email'], password_hash=hashed_pw, role='doctor')
        db.session.add(new_user)
        db.session.flush() 

        new_doctor = Doctor(
            user_id=new_user.id,
            full_name=data['name'],
            experience=int(data.get('experience', 0)),
            department_name=data['department'],
            contact=data.get('contact'),
            bio=data.get('bio'),
            fee=float(data.get('fee', 0.0)),
            is_blacklisted=False,
            # FIXED: Assigning directly to model fields
            timings=data.get('timings', '09:00 AM - 05:00 PM'),
            days=data.get('days', 'Mon - Fri')
        )
        
        db.session.add(new_doctor)
        db.session.commit()
        return jsonify({"message": "Doctor added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# --- GET ALL DOCTORS (ADMIN VIEW) ---
@app.route('/api/admin/doctors', methods=['GET'])
@jwt_required()
def get_admin_doctors():
    doctors = Doctor.query.all()
    result = []
    for doc in doctors:
        result.append({
            "id": doc.id,
            "name": doc.full_name,
            "username": doc.user.username,
            "experience": doc.experience,
            "email": doc.user.email,
            "department": doc.department_name,
            "contact": doc.contact,
            "bio": doc.bio,
            "fee": doc.fee,
            # FIXED: Accessing the correct model fields directly
            "timings": doc.timings, 
            "days": doc.days, 
            "is_blacklisted": doc.is_blacklisted
        })
    return jsonify(result), 200

# --- UPDATE DOCTOR ---
@app.route('/api/admin/update_doctor/<int:id>', methods=['PUT'])
@jwt_required()
def update_doctor(id):
    doctor = Doctor.query.get(id)
    if not doctor: return jsonify({"error": "Doctor not found"}), 404
    
    data = request.get_json()
    
    try:
        # Update Doctor Fields
        doctor.full_name = data.get('name', doctor.full_name)
        doctor.experience = int(data.get('experience', doctor.experience))
        doctor.department_name = data.get('department', doctor.department_name)
        doctor.contact = data.get('contact', doctor.contact)
        doctor.bio = data.get('bio', doctor.bio)
        doctor.fee = float(data.get('fee', doctor.fee))
        
        # FIXED: Directly update the 'timings' and 'days' fields
        doctor.timings = data.get('timings', doctor.timings)
        doctor.days = data.get('days', doctor.days)
        
        # Update User Fields
        if data.get('email'): doctor.user.email = data.get('email')
        if data.get('username'): doctor.user.username = data.get('username')

        db.session.commit()
        return jsonify({"message": "Doctor updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# --- NEW: DELETE DOCTOR ---
@app.route('/api/admin/delete_doctor/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(id):
    doctor = Doctor.query.get(id)
    if not doctor: return jsonify({"error": "Doctor not found"}), 404
    
    try:
        user = doctor.user # Get associated user account
        db.session.delete(doctor) # Delete profile
        if user: db.session.delete(user) # Delete login account
        
        db.session.commit()
        return jsonify({"message": "Doctor deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# --- NEW: TOGGLE BLACKLIST STATUS ---
@app.route('/api/admin/blacklist_doctor/<int:id>', methods=['PUT'])
@jwt_required()
def toggle_blacklist_doctor(id):
    doctor = Doctor.query.get(id)
    if not doctor: return jsonify({"error": "Doctor not found"}), 404
    
    try:
        # Flip the boolean status
        doctor.is_blacklisted = not doctor.is_blacklisted
        db.session.commit()
        
        status = "Blacklisted" if doctor.is_blacklisted else "Restored"
        return jsonify({"message": f"Doctor {status} successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/add_department', methods=['POST'])
@jwt_required()
def add_department():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({"error": "Department name is required"}), 400
        
    if Department.query.filter_by(name=data['name']).first():
        return jsonify({"error": "Department already exists"}), 400

    try:
        new_dept = Department(
            name=data['name'],
            description=data.get('desc', ''),
            icon=data.get('icon', 'bi-hospital')
        )
        db.session.add(new_dept)
        db.session.commit()
        return jsonify({"message": "Department created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# UPDATE Department
@app.route('/api/admin/update_department/<int:id>', methods=['PUT'])
@jwt_required()
def update_department(id):
    dept = Department.query.get_or_404(id)
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({"error": "Department name is required"}), 400

    try:
        dept.name = data['name']
        dept.description = data.get('desc', dept.description)
        dept.icon = data.get('icon', dept.icon)
        
        db.session.commit()
        return jsonify({"message": "Department updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/delete_department/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_department(id):
    try:
        dept = Department.query.get_or_404(id)
        db.session.delete(dept)
        db.session.commit()
        return jsonify({"message": "Department deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- ADMIN: GET ALL APPOINTMENTS (For AppointmentsView.vue) ---
@app.route('/api/admin/appointments', methods=['GET'])
@jwt_required()
def get_admin_appointments():
    # Join with Patient and Doctor to get names
    appointments = Appointment.query.all()
    result = []
    for appt in appointments:
        result.append({
            "id": appt.id,
            "patient": appt.patient.full_name,
            "doctor": appt.doctor.full_name,
            "dept": appt.doctor.department_name,
            "date": appt.date_str,
            "time": appt.time_slot,
            "status": appt.status
        })
    # Sort by ID desc (newest first)
    result.sort(key=lambda x: x['id'], reverse=True)
    return jsonify(result), 200

# --- ADMIN: GET ALL MEDICAL RECORDS (For MedicalRecords.vue) ---
@app.route('/api/admin/medical_records', methods=['GET'])
@jwt_required()
def get_admin_medical_records():
    records = MedicalRecord.query.all()
    result = []
    
    for rec in records:
        # Calculate Age from DOB
        dob = rec.appointment.patient.dob
        age = "N/A"
        if dob:
            try:
                birth_date = datetime.strptime(dob, "%Y-%m-%d")
                today = datetime.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            except:
                pass

        result.append({
            "id": f"REC-{rec.id:04d}", # Format as REC-0001
            "db_id": rec.id, # Real ID for logic
            "patient": rec.appointment.patient.full_name,
            "age": age,
            "doctor": rec.appointment.doctor.full_name,
            "dept": rec.appointment.doctor.department_name,
            "diagnosis": rec.diagnosis,
            "date": rec.appointment.date_str,
            "prescription": rec.prescription,
            "tests": rec.tests,
            "notes": rec.notes
        })
    
    # Sort newest first
    result.sort(key=lambda x: x['db_id'], reverse=True)
    return jsonify(result), 200

# --- ADMIN: DASHBOARD STATS ---
@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    return jsonify({
        "patients": User.query.filter_by(role='patient').count(),
        "doctors": Doctor.query.count(),
        "appointments": Appointment.query.count(),
        "departments": Department.query.count()
    }), 200

# ==========================================
# 3. DOCTOR ROUTES (Dashboard, Actions)
# ==========================================

# --- DOCTOR PROFILE (GET/PUT) ---
@app.route('/api/doctor/profile', methods=['GET', 'PUT'])
@jwt_required()
def handle_doctor_profile():
    current_user_id = get_jwt_identity()
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    if not doctor:
        return jsonify({"error": "Profile not found"}), 404

    # --- GET PROFILE ---
    if request.method == 'GET':
        return jsonify({
            "id": doctor.id,
            "name": doctor.full_name,
            "email": doctor.user.email,
            "department": doctor.department_name,
            "contact": doctor.contact,
            "fee": doctor.fee,
            "bio": doctor.bio,
            "timings": doctor.timings,  # FIXED
            "days": doctor.days         # FIXED
        }), 200
    
    # --- UPDATE PROFILE ---
    if request.method == 'PUT':
        data = request.get_json()
        
        doctor.full_name = data.get('name', doctor.full_name)
        doctor.contact = data.get('contact', doctor.contact)
        doctor.fee = float(data.get('fee', doctor.fee))
        
        # FIXED: Update directly without hasattr check (columns exist in model)
        doctor.timings = data.get('timings', doctor.timings)
        doctor.days = data.get('days', doctor.days)
        
        if data.get('email'):
            doctor.user.email = data.get('email')
        
        try:
            db.session.commit()
            return jsonify({"message": "Profile updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@app.route('/api/doctor/appointments', methods=['GET'])
@jwt_required()
def get_doctor_appointments():
    current_user_id = get_jwt_identity()
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({"error": "Doctor profile not found"}), 404

    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    
    scheduled = []
    completed = []

    for appt in appointments:
        data = {
            "id": appt.id,
            "patient": appt.patient.full_name,
            "patient_id": appt.patient.id,
            "date": appt.date_str,
            "time": appt.time_slot,
            "status": appt.status
        }

        if appt.status == 'Scheduled':
            data["reason"] = appt.symptoms or "Routine Checkup"
            scheduled.append(data)
        elif appt.status == 'Completed':
            record = appt.medical_record
            data["diagnosis"] = record.diagnosis if record else "No diagnosis"
            data["prescription"] = record.prescription if record else ""
            data["tests"] = record.tests if record else "None"
            completed.append(data)
            
    return jsonify({"scheduled": scheduled, "completed": completed}), 200

@app.route('/api/doctor/complete_appointment', methods=['POST'])
@jwt_required()
def complete_appointment():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    appt = Appointment.query.get(data.get('appointment_id'))
    
    if not appt or appt.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        new_record = MedicalRecord(
            appointment_id=appt.id,
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            tests=data.get('tests'),
            notes=data.get('notes')
        )
        db.session.add(new_record)
        appt.status = 'Completed'
        db.session.commit()
        return jsonify({"message": "Appointment completed"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/doctor/cancel_appointment/<int:id>', methods=['PUT'])
@jwt_required()
def doctor_cancel_appointment(id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    appt = Appointment.query.get(id)
    
    if not appt or appt.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        appt.status = 'Cancelled'
        appt.remarks = data.get('reason', 'Cancelled by Doctor') 
        db.session.commit()
        return jsonify({"message": "Appointment cancelled"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/doctor/reschedule_appointment/<int:id>', methods=['PUT'])
@jwt_required()
def doctor_reschedule_appointment(id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    appt = Appointment.query.get(id)
    
    if not appt or appt.doctor_id != doctor.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Check for conflicts
    conflict = Appointment.query.filter_by(
        doctor_id=doctor.id, 
        date_str=data['date'], 
        time_slot=data['slot']
    ).filter(Appointment.status != 'Cancelled').first()

    if conflict:
        return jsonify({"error": "Slot already booked"}), 409

    try:
        appt.date_str = data['date']
        appt.time_slot = data['slot']
        appt.remarks = f"Rescheduled: {data.get('reason', 'No reason provided')}"
        appt.status = 'Scheduled'
        db.session.commit()
        return jsonify({"message": "Rescheduled successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 4. PATIENT ROUTES (Booking, Profile)
# ==========================================

@app.route('/api/patient/global_search', methods=['GET'])
@jwt_required()
def patient_global_search():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({}) 
    
    search_term = f"%{query}%"

    doctors = Doctor.query.filter(
        (Doctor.full_name.ilike(search_term)) |
        (Doctor.department_name.ilike(search_term))
    ).all()

    depts = Department.query.filter(Department.name.ilike(search_term)).all()

    return jsonify({
        "doctors": [{"id": d.id, "name": d.full_name, "dept": d.department_name} for d in doctors],
        "departments": [{"id": d.id, "name": d.name} for d in depts]
    }), 200

@app.route('/api/book_appointment', methods=['POST'])
@jwt_required()
def book_appointment():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 1. Get Patient
    patient = Patient.query.filter_by(user_id=current_user_id).first()
    if not patient: 
        return jsonify({"error": "Patient not found"}), 404

    # 2. Validate Data
    if not data.get('doctor_id') or not data.get('date') or not data.get('slot'):
        return jsonify({"error": "Missing booking details"}), 400

    # --- 3. THE FIX: FINAL AVAILABILITY CHECK ---
    # We check one last time if this slot is taken by a non-cancelled appointment
    conflict = Appointment.query.filter_by(
        doctor_id=data['doctor_id'], 
        date_str=data['date'], 
        time_slot=data['slot']
    ).filter(Appointment.status != 'Cancelled').first()

    if conflict:
        return jsonify({"error": "This slot was just booked by another patient. Please choose another."}), 409
    # ----------------------------------------------

    try:
        new_appt = Appointment(
            patient_id=patient.id,
            doctor_id=data['doctor_id'],
            date_str=data['date'],
            time_slot=data['slot'],
            symptoms=data.get('symptoms', ''),
            status='Scheduled'
        )
        db.session.add(new_appt)
        db.session.commit()
        return jsonify({"message": "Booked successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/cancel_appointment/<int:id>', methods=['PUT'])
@jwt_required()
def cancel_appointment_patient(id):
    current_user_id = get_jwt_identity()
    patient = Patient.query.filter_by(user_id=current_user_id).first()
    appt = Appointment.query.get(id)
    
    if not appt or appt.patient_id != patient.id:
        return jsonify({"error": "Unauthorized"}), 404

    try:
        appt.status = 'Cancelled'
        appt.remarks = "Cancelled by Patient"
        db.session.commit()
        return jsonify({"message": "Cancelled successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/my_appointments', methods=['GET'])
@jwt_required()
def get_my_appointments():
    current_user_id = get_jwt_identity()
    patient = Patient.query.filter_by(user_id=current_user_id).first()
    if not patient: return jsonify({"error": "Patient not found"}), 404

    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    result = []
    for appt in appointments:
        result.append({
            "id": appt.id,
            "doctor": appt.doctor.full_name,
            "dept": appt.doctor.department_name,
            "date": appt.date_str,
            "time": appt.time_slot,
            "status": appt.status,
            "remarks": appt.remarks, 
            "has_record": True if appt.medical_record else False 
        })
    # Sort by ID descending (Creation time)
    result.sort(key=lambda x: x['id'], reverse=True)
    return jsonify(result), 200

@app.route('/api/patient/profile', methods=['GET', 'PUT'])
@jwt_required()
def handle_patient_profile():
    current_user_id = get_jwt_identity()
    patient = Patient.query.filter_by(user_id=current_user_id).first()
    
    if not patient: return jsonify({"error": "Profile not found"}), 404

    if request.method == 'GET':
        return jsonify({
            "name": patient.full_name,
            "email": patient.user.email,
            "username": patient.user.username,
            "phone": patient.phone,
            "dob": patient.dob
        }), 200
    
    if request.method == 'PUT':
        data = request.get_json()
        patient.full_name = data.get('name', patient.full_name)
        patient.phone = data.get('phone', patient.phone)
        patient.dob = data.get('dob', patient.dob)
        if data.get('email'):
            patient.user.email = data.get('email')
        
        try:
            db.session.commit()
            return jsonify({"message": "Profile updated"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# ==========================================
# 5. PUBLIC / SHARED DATA ROUTES
# ==========================================

@app.route('/api/doctors', methods=['GET'])
def get_all_doctors():
    doctors = Doctor.query.filter_by(is_blacklisted=False).all()
    result = [{
        "id": doc.id,
        "name": doc.full_name,
        "exp": doc.experience,
        "dept": doc.department_name,
        "bio": doc.bio,
        "image": doc.image_file,
        "fee": doc.fee,
        # ADDED THESE TWO FIELDS
        "timings": getattr(doc, 'timings', '09:00 AM - 05:00 PM'),
        "days": getattr(doc, 'days', 'Mon - Fri')
    } for doc in doctors]
    return jsonify(result), 200

@app.route('/api/departments', methods=['GET'])
def get_departments():
    depts = Department.query.all()
    return jsonify([{
        "id": d.id, "name": d.name, "desc": d.description, "icon": d.icon
    } for d in depts]), 200

# Slot Generation & Availability Check
@app.route('/api/appointments/available_slots', methods=['POST'])
def get_available_slots():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date_str = data.get('date') # Expected "YYYY-MM-DD"
    
    if not doctor_id or not date_str: return jsonify({"error": "Missing params"}), 400

    doctor = Doctor.query.get(doctor_id)
    if not doctor: return jsonify({"error": "Doctor not found"}), 404

    # 1. Parse Date
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return jsonify({"error": "Invalid date format"}), 400

    # 2. CHECK WORKING DAYS (Uses new helper)
    if not is_working_day(target_date, doctor.days):
        return jsonify({
            "error": f"Dr. {doctor.full_name} is not available on {target_date.strftime('%A')}s",
            "slots": [] 
        }), 200

    # 3. Generate Slots
    try: start_time, end_time = doctor.timings.split(' - ')
    except: start_time, end_time = "09:00 AM", "05:00 PM"

    all_slots = generate_slots(start_time, end_time)
    
    # 4. Filter Booked
    booked_appts = Appointment.query.filter_by(
        doctor_id=doctor_id, date_str=date_str
    ).filter(Appointment.status != 'Cancelled').all()
    
    booked_times = [appt.time_slot for appt in booked_appts]

    # 5. Filter Past Times (Today Logic)
    current_dt = datetime.now()
    is_today = date_str == current_dt.strftime('%Y-%m-%d')
    
    final_slots = []
    for slot in all_slots:
        is_taken = slot in booked_times
        if not is_taken and is_today:
            try:
                slot_dt = datetime.strptime(f"{date_str} {slot}", "%Y-%m-%d %I:%M %p")
                if slot_dt < current_dt: is_taken = True 
            except: pass

        final_slots.append({"time": slot, "is_booked": is_taken})
    
    return jsonify(final_slots), 200

@app.route('/api/appointments/check_availability', methods=['POST'])
def check_availability():
    """ Simple returns list of booked times (for legacy frontend support) """
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date_str = data.get('date')
    
    booked_appts = Appointment.query.filter_by(doctor_id=doctor_id, date_str=date_str).filter(Appointment.status != 'Cancelled').all()
    return jsonify([appt.time_slot for appt in booked_appts]), 200

# ==========================================
# 6. ERROR HANDLERS
# ==========================================

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"!!! JWT INVALID TOKEN: {error} !!!") 
    return jsonify({"message": "Signature validation failed", "error": error}), 422

if __name__ == '__main__':
    app.run(debug=True, port=5000)