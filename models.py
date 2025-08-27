from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='client')  # admin, judge, lawyer, client, student
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cases_as_lawyer = db.relationship('Case', foreign_keys='Case.lawyer_id', backref='lawyer', lazy='dynamic')
    cases_as_client = db.relationship('Case', foreign_keys='Case.client_id', backref='client', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='user', lazy='dynamic')
    documents = db.relationship('Document', backref='uploaded_by_user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Court(db.Model):
    __tablename__ = 'courts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    court_type = db.Column(db.String(50), nullable=False)  # محكمة ابتدائية، استئناف، etc.
    governorate = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    working_hours = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cases = db.relationship('Case', backref='court', lazy='dynamic')

class LawyerProfile(db.Model):
    __tablename__ = 'lawyer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer)
    law_firm = db.Column(db.String(200))
    office_address = db.Column(db.Text)
    consultation_fee = db.Column(db.Float)
    bio = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='lawyer_profile')

class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    case_type = db.Column(db.String(50), nullable=False)  # مدني، جنائي، تجاري، etc.
    status = db.Column(db.String(30), nullable=False, default='active')  # active, closed, pending
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    
    # Foreign Keys
    lawyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'))
    
    # Dates
    filed_date = db.Column(db.Date, nullable=False)
    last_hearing_date = db.Column(db.Date)
    next_hearing_date = db.Column(db.Date)
    closed_date = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='case', lazy='dynamic')
    appointments = db.relationship('Appointment', backref='case', lazy='dynamic')
    case_updates = db.relationship('CaseUpdate', backref='case', lazy='dynamic')

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    document_type = db.Column(db.String(50), nullable=False)  # template, evidence, contract, etc.
    
    # Foreign Keys
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    is_template = db.Column(db.Boolean, default=False)
    template_category = db.Column(db.String(50))  # دعوى، عقد، etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DocumentTemplate(db.Model):
    __tablename__ = 'document_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # دعوى، عقد، مذكرة، etc.
    description = db.Column(db.Text)
    template_content = db.Column(db.Text, nullable=False)
    template_fields = db.Column(db.Text)  # JSON of fillable fields
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_templates')

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    appointment_type = db.Column(db.String(50), nullable=False)  # hearing, meeting, deadline, etc.
    
    # Date and time
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime)
    is_all_day = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    
    # Reminder settings
    reminder_minutes = db.Column(db.Integer, default=60)
    reminder_sent = db.Column(db.Boolean, default=False)
    
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    location = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CaseUpdate(db.Model):
    __tablename__ = 'case_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    update_type = db.Column(db.String(50), nullable=False)  # status_change, hearing, document, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='case_updates')

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # reminder, update, system, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
