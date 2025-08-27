import os
import uuid
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask import current_app
import json

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder='uploads'):
    """Save uploaded file and return filename and path"""
    if file and file.filename:
        # Create upload directory if it doesn't exist
        upload_path = os.path.join(current_app.root_path, upload_folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return unique_filename, file_path
    return None, None

def format_file_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

def arabic_date_format(date_obj):
    """Format date in Arabic"""
    if not date_obj:
        return ""
    
    if isinstance(date_obj, str):
        return date_obj
    
    months_arabic = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    
    if isinstance(date_obj, datetime):
        return f"{date_obj.day} {months_arabic[date_obj.month]} {date_obj.year}"
    elif isinstance(date_obj, date):
        return f"{date_obj.day} {months_arabic[date_obj.month]} {date_obj.year}"
    
    return str(date_obj)

def generate_case_number():
    """Generate unique case number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = uuid.uuid4().hex[:6].upper()
    return f"CASE-{timestamp}-{random_suffix}"

def get_governorates():
    """Get list of Yemeni governorates"""
    return [
        'صنعاء', 'عدن', 'تعز', 'الحديدة', 'إب', 'ذمار',
        'حضرموت', 'لحج', 'أبين', 'شبوة', 'مأرب', 'الجوف',
        'صعدة', 'حجة', 'المهرة', 'عمران', 'الضالع', 'ريمة',
        'البيضاء', 'سقطرى'
    ]

def get_case_types():
    """Get case types in Arabic"""
    return [
        'مدني', 'جنائي', 'تجاري', 'عمالي', 'أحوال شخصية',
        'إداري', 'عقاري', 'ضرائب', 'دستوري'
    ]

def get_court_types():
    """Get court types in Arabic"""
    return [
        'ابتدائية', 'استئناف', 'عليا', 'تجارية', 'جنائية', 'أحوال شخصية'
    ]

def process_template_fields(template_content):
    """Extract fillable fields from template content"""
    import re
    
    # Find fields marked with {{field_name}}
    pattern = r'\{\{([^}]+)\}\}'
    fields = re.findall(pattern, template_content)
    
    field_definitions = []
    for field in fields:
        field_definitions.append({
            'name': field.strip(),
            'label': field.strip().replace('_', ' '),
            'type': 'text',
            'required': True
        })
    
    return json.dumps(field_definitions)

def fill_template(template_content, field_values):
    """Fill template with provided values"""
    for field_name, value in field_values.items():
        placeholder = f"{{{{{field_name}}}}}"
        template_content = template_content.replace(placeholder, str(value))
    
    return template_content

def get_role_display_name(role):
    """Get Arabic display name for user role"""
    role_names = {
        'client': 'متقاض',
        'lawyer': 'محامي',
        'judge': 'قاضي',
        'student': 'طالب قانون',
        'admin': 'مدير النظام'
    }
    return role_names.get(role, role)

def get_status_display_name(status):
    """Get Arabic display name for case status"""
    status_names = {
        'active': 'نشطة',
        'pending': 'معلقة',
        'closed': 'مغلقة',
        'on_hold': 'مؤجلة',
        'appeal': 'استئناف'
    }
    return status_names.get(status, status)

def calculate_case_age_days(filed_date):
    """Calculate case age in days"""
    if not filed_date:
        return 0
    
    if isinstance(filed_date, str):
        filed_date = datetime.strptime(filed_date, '%Y-%m-%d').date()
    
    today = date.today()
    return (today - filed_date).days

def get_priority_color(priority):
    """Get color class for priority"""
    colors = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'success'
    }
    return colors.get(priority, 'secondary')

def paginate_query(query, page=1, per_page=20):
    """Helper function for pagination"""
    return query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )

# Admin utility functions
def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    from flask import abort
    from flask_login import current_user
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def get_system_stats():
    """Get system statistics for admin dashboard"""
    from models import User, Case, Court, LawyerProfile, Appointment
    
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_cases': Case.query.count(),
        'active_cases': Case.query.filter_by(status='active').count(),
        'total_courts': Court.query.count(),
        'active_courts': Court.query.filter_by(is_active=True).count(),
        'total_lawyers': LawyerProfile.query.count(),
        'verified_lawyers': LawyerProfile.query.filter_by(is_verified=True).count(),
        'total_appointments': Appointment.query.count(),
        'pending_appointments': Appointment.query.filter_by(status='scheduled').count()
    }
    
    return stats

def create_admin_user():
    """Create default admin user if none exists"""
    from models import User
    from app import db
    
    try:
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@system.local',
                first_name='مدير',
                last_name='النظام',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            return admin
    except Exception as e:
        print(f"Admin user may already exist: {e}")
        db.session.rollback()
    return None

def log_admin_activity(action, description, user_id=None):
    """Log admin activities for audit trail"""
    from flask_login import current_user
    from models import Notification
    from app import db
    
    if not user_id:
        user_id = current_user.id if current_user.is_authenticated else None
    
    if user_id:
        notification = Notification(
            user_id=user_id,
            title=f'إجراء إداري: {action}',
            message=description,
            notification_type='admin_activity'
        )
        db.session.add(notification)
        db.session.commit()
