import os
from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from sqlalchemy import or_, desc, func
from app import app, db
from models import *
from forms import *
from utils import *

# Jinja2 template filters
@app.template_filter('arabic_date')
def arabic_date_filter(date_obj):
    return arabic_date_format(date_obj)

@app.template_filter('role_name')
def role_name_filter(role):
    return get_role_display_name(role)

@app.template_filter('status_name')
def status_name_filter(status):
    return get_status_display_name(status)

@app.template_filter('priority_color')
def priority_color_filter(priority):
    return get_priority_color(priority)

@app.template_filter('file_size')
def file_size_filter(bytes):
    return format_file_size(bytes)

# Main routes
@app.route('/')
def index():
    """Home page with dashboard"""
    if current_user.is_authenticated:
        # Dashboard data based on user role
        if current_user.role == 'lawyer':
            recent_cases = Case.query.filter_by(lawyer_id=current_user.id).order_by(desc(Case.created_at)).limit(5).all()
            upcoming_appointments = Appointment.query.filter_by(user_id=current_user.id).filter(
                Appointment.start_datetime >= datetime.now()
            ).order_by(Appointment.start_datetime).limit(5).all()
            
            stats = {
                'total_cases': Case.query.filter_by(lawyer_id=current_user.id).count(),
                'active_cases': Case.query.filter_by(lawyer_id=current_user.id, status='active').count(),
                'pending_cases': Case.query.filter_by(lawyer_id=current_user.id, status='pending').count(),
                'total_documents': Document.query.filter_by(uploaded_by=current_user.id).count()
            }
            
        elif current_user.role == 'client':
            recent_cases = Case.query.filter_by(client_id=current_user.id).order_by(desc(Case.created_at)).limit(5).all()
            upcoming_appointments = Appointment.query.join(Case).filter(
                Case.client_id == current_user.id,
                Appointment.start_datetime >= datetime.now()
            ).order_by(Appointment.start_datetime).limit(5).all()
            
            stats = {
                'total_cases': Case.query.filter_by(client_id=current_user.id).count(),
                'active_cases': Case.query.filter_by(client_id=current_user.id, status='active').count(),
                'pending_cases': Case.query.filter_by(client_id=current_user.id, status='pending').count(),
                'total_documents': Document.query.join(Case).filter(Case.client_id == current_user.id).count()
            }
        else:
            recent_cases = []
            upcoming_appointments = []
            stats = {}
        
        return render_template('index.html', 
                             recent_cases=recent_cases,
                             upcoming_appointments=upcoming_appointments,
                             stats=stats)
    else:
        return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            flash('تم تسجيل الدخول بنجاح', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            or_(User.username == form.username.data, User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل', 'danger')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash('تم إنشاء الحساب بنجاح', 'success')
            return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('index'))

# Court directory routes
@app.route('/courts')
def courts():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    governorate = request.args.get('governorate', '')
    court_type = request.args.get('court_type', '')
    
    query = Court.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            or_(Court.name.contains(search), 
                Court.city.contains(search),
                Court.address.contains(search))
        )
    
    if governorate:
        query = query.filter_by(governorate=governorate)
    
    if court_type:
        query = query.filter_by(court_type=court_type)
    
    courts = query.order_by(Court.governorate, Court.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('courts/directory.html', 
                         courts=courts,
                         search=search,
                         governorate=governorate,
                         court_type=court_type,
                         governorates=get_governorates(),
                         court_types=get_court_types())

@app.route('/courts/add', methods=['GET', 'POST'])
@login_required
def add_court():
    if current_user.role not in ['admin', 'judge']:
        flash('ليس لديك صلاحية لإضافة محكمة', 'danger')
        return redirect(url_for('courts'))
    
    form = CourtForm()
    if form.validate_on_submit():
        court = Court(
            name=form.name.data,
            name_en=form.name_en.data,
            court_type=form.court_type.data,
            governorate=form.governorate.data,
            city=form.city.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            working_hours=form.working_hours.data
        )
        db.session.add(court)
        db.session.commit()
        flash('تم إضافة المحكمة بنجاح', 'success')
        return redirect(url_for('courts'))
    
    return render_template('courts/add.html', form=form)

# Lawyer directory routes
@app.route('/lawyers')
def lawyers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')
    governorate = request.args.get('governorate', '')
    
    query = db.session.query(User, LawyerProfile).join(LawyerProfile).filter(
        User.role == 'lawyer',
        User.is_active == True,
        LawyerProfile.is_verified == True
    )
    
    if search:
        query = query.filter(
            or_(User.first_name.contains(search),
                User.last_name.contains(search),
                LawyerProfile.law_firm.contains(search))
        )
    
    if specialization:
        query = query.filter(LawyerProfile.specialization == specialization)
    
    lawyers = query.order_by(LawyerProfile.rating.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    specializations = ['مدني', 'جنائي', 'تجاري', 'عمالي', 'أحوال_شخصية', 'إداري', 'دستوري', 'دولي', 'عقاري', 'ضرائب']
    
    return render_template('lawyers/directory.html',
                         lawyers=lawyers,
                         search=search,
                         specialization=specialization,
                         governorate=governorate,
                         specializations=specializations,
                         governorates=get_governorates())

@app.route('/lawyers/profile')
@login_required
def lawyer_profile():
    if current_user.role != 'lawyer':
        flash('هذه الصفحة مخصصة للمحامين فقط', 'danger')
        return redirect(url_for('index'))
    
    profile = LawyerProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('lawyers/profile.html', profile=profile)

@app.route('/lawyers/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_lawyer_profile():
    if current_user.role != 'lawyer':
        flash('هذه الصفحة مخصصة للمحامين فقط', 'danger')
        return redirect(url_for('index'))
    
    profile = LawyerProfile.query.filter_by(user_id=current_user.id).first()
    form = LawyerProfileForm(obj=profile)
    
    if form.validate_on_submit():
        if not profile:
            profile = LawyerProfile(user_id=current_user.id)
        
        form.populate_obj(profile)
        db.session.add(profile)
        db.session.commit()
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        return redirect(url_for('lawyer_profile'))
    
    return render_template('lawyers/edit_profile.html', form=form, profile=profile)

# Case management routes
@app.route('/cases')
@login_required
def cases():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    case_type = request.args.get('case_type', '')
    
    if current_user.role == 'lawyer':
        query = Case.query.filter_by(lawyer_id=current_user.id)
    elif current_user.role == 'client':
        query = Case.query.filter_by(client_id=current_user.id)
    else:
        query = Case.query
    
    if status:
        query = query.filter_by(status=status)
    
    if case_type:
        query = query.filter_by(case_type=case_type)
    
    cases = query.order_by(desc(Case.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('cases/dashboard.html',
                         cases=cases,
                         status=status,
                         case_type=case_type,
                         case_types=get_case_types())

@app.route('/cases/create', methods=['GET', 'POST'])
@login_required
def create_case():
    if current_user.role not in ['lawyer', 'admin']:
        flash('ليس لديك صلاحية لإنشاء قضية', 'danger')
        return redirect(url_for('cases'))
    
    form = CaseForm()
    
    # Populate client choices
    clients = User.query.filter_by(role='client', is_active=True).all()
    form.client_id.choices = [(u.id, u.full_name) for u in clients]
    
    # Populate court choices
    courts = Court.query.filter_by(is_active=True).all()
    form.court_id.choices = [(0, 'اختر المحكمة')] + [(c.id, c.name) for c in courts]
    
    if form.validate_on_submit():
        case = Case(
            case_number=form.case_number.data,
            title=form.title.data,
            description=form.description.data,
            case_type=form.case_type.data,
            lawyer_id=current_user.id,
            client_id=form.client_id.data,
            court_id=form.court_id.data if form.court_id.data != 0 else None,
            priority=form.priority.data,
            filed_date=form.filed_date.data,
            next_hearing_date=form.next_hearing_date.data
        )
        db.session.add(case)
        db.session.commit()
        
        # Create initial case update
        update = CaseUpdate(
            case_id=case.id,
            update_type='creation',
            title='إنشاء القضية',
            description='تم إنشاء القضية بنجاح',
            created_by=current_user.id
        )
        db.session.add(update)
        db.session.commit()
        
        flash('تم إنشاء القضية بنجاح', 'success')
        return redirect(url_for('view_case', id=case.id))
    
    # Auto-generate case number
    if not form.case_number.data:
        form.case_number.data = generate_case_number()
    
    return render_template('cases/create.html', form=form)

@app.route('/cases/<int:id>')
@login_required
def view_case(id):
    case = Case.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'lawyer' and case.lawyer_id != current_user.id:
        flash('ليس لديك صلاحية لعرض هذه القضية', 'danger')
        return redirect(url_for('cases'))
    elif current_user.role == 'client' and case.client_id != current_user.id:
        flash('ليس لديك صلاحية لعرض هذه القضية', 'danger')
        return redirect(url_for('cases'))
    
    # Get case updates
    updates = CaseUpdate.query.filter_by(case_id=case.id).order_by(desc(CaseUpdate.created_at)).all()
    
    # Get case documents
    documents = Document.query.filter_by(case_id=case.id).order_by(desc(Document.created_at)).all()
    
    # Get case appointments
    appointments = Appointment.query.filter_by(case_id=case.id).order_by(Appointment.start_datetime).all()
    
    return render_template('cases/view.html',
                         case=case,
                         updates=updates,
                         documents=documents,
                         appointments=appointments)

# Document templates routes
@app.route('/documents/templates')
@login_required
def document_templates():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    
    query = DocumentTemplate.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    templates = query.order_by(DocumentTemplate.category, DocumentTemplate.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = ['دعوى', 'عقد', 'مذكرة', 'طلب', 'توكيل', 'إقرار', 'شهادة']
    
    return render_template('documents/templates.html',
                         templates=templates,
                         category=category,
                         categories=categories)

@app.route('/documents/templates/create', methods=['GET', 'POST'])
@login_required
def create_document_template():
    if current_user.role not in ['lawyer', 'admin']:
        flash('ليس لديك صلاحية لإنشاء نموذج', 'danger')
        return redirect(url_for('document_templates'))
    
    form = DocumentTemplateForm()
    if form.validate_on_submit():
        template = DocumentTemplate(
            name=form.name.data,
            category=form.category.data,
            description=form.description.data,
            template_content=form.template_content.data,
            template_fields=process_template_fields(form.template_content.data),
            created_by=current_user.id
        )
        db.session.add(template)
        db.session.commit()
        flash('تم إنشاء النموذج بنجاح', 'success')
        return redirect(url_for('document_templates'))
    
    return render_template('documents/create.html', form=form)

# Calendar routes
@app.route('/calendar')
@login_required
def calendar():
    # Get appointments for current user
    if current_user.role == 'lawyer':
        appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    elif current_user.role == 'client':
        appointments = Appointment.query.join(Case).filter(Case.client_id == current_user.id).all()
    else:
        appointments = []
    
    # Convert appointments to calendar events format
    events = []
    for appointment in appointments:
        events.append({
            'id': appointment.id,
            'title': appointment.title,
            'start': appointment.start_datetime.isoformat(),
            'end': appointment.end_datetime.isoformat() if appointment.end_datetime else None,
            'allDay': appointment.is_all_day,
            'backgroundColor': '#007bff' if appointment.appointment_type == 'hearing' else '#28a745'
        })
    
    return render_template('calendar/calendar.html', events=events)

@app.route('/calendar/appointments/create', methods=['GET', 'POST'])
@login_required
def create_appointment():
    form = AppointmentForm()
    
    # Populate case choices for lawyers
    if current_user.role == 'lawyer':
        cases = Case.query.filter_by(lawyer_id=current_user.id, status='active').all()
        form.case_id.choices = [(0, 'اختر القضية')] + [(c.id, f"{c.case_number} - {c.title}") for c in cases]
    
    if form.validate_on_submit():
        start_datetime = datetime.fromisoformat(form.start_datetime.data)
        end_datetime = datetime.fromisoformat(form.end_datetime.data) if form.end_datetime.data else None
        
        appointment = Appointment(
            title=form.title.data,
            description=form.description.data,
            appointment_type=form.appointment_type.data,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            is_all_day=form.is_all_day.data,
            user_id=current_user.id,
            case_id=form.case_id.data if form.case_id.data != 0 else None,
            location=form.location.data,
            reminder_minutes=form.reminder_minutes.data
        )
        db.session.add(appointment)
        db.session.commit()
        flash('تم إنشاء الموعد بنجاح', 'success')
        return redirect(url_for('calendar'))
    
    return render_template('calendar/create_appointment.html', form=form)

# Client portal routes
@app.route('/client/portal')
@login_required
def client_portal():
    if current_user.role != 'client':
        flash('هذه الصفحة مخصصة للعملاء فقط', 'danger')
        return redirect(url_for('index'))
    
    # Get client's cases
    cases = Case.query.filter_by(client_id=current_user.id).order_by(desc(Case.created_at)).all()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.join(Case).filter(
        Case.client_id == current_user.id,
        Appointment.start_datetime >= datetime.now()
    ).order_by(Appointment.start_datetime).limit(5).all()
    
    # Get recent notifications
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        desc(Notification.created_at)
    ).limit(10).all()
    
    return render_template('client/portal.html',
                         cases=cases,
                         upcoming_appointments=upcoming_appointments,
                         notifications=notifications)

# Reports routes
@app.route('/reports')
@login_required
def reports():
    if current_user.role not in ['lawyer', 'admin']:
        flash('ليس لديك صلاحية لعرض التقارير', 'danger')
        return redirect(url_for('index'))
    
    # Basic statistics
    if current_user.role == 'lawyer':
        total_cases = Case.query.filter_by(lawyer_id=current_user.id).count()
        active_cases = Case.query.filter_by(lawyer_id=current_user.id, status='active').count()
        closed_cases = Case.query.filter_by(lawyer_id=current_user.id, status='closed').count()
        
        # Cases by type
        case_types = db.session.query(
            Case.case_type,
            func.count(Case.id).label('count')
        ).filter_by(lawyer_id=current_user.id).group_by(Case.case_type).all()
        
    else:  # admin
        total_cases = Case.query.count()
        active_cases = Case.query.filter_by(status='active').count()
        closed_cases = Case.query.filter_by(status='closed').count()
        
        case_types = db.session.query(
            Case.case_type,
            func.count(Case.id).label('count')
        ).group_by(Case.case_type).all()
    
    stats = {
        'total_cases': total_cases,
        'active_cases': active_cases,
        'closed_cases': closed_cases,
        'case_types': case_types
    }
    
    return render_template('reports/dashboard.html', stats=stats)

# Search routes
@app.route('/search')
def search():
    form = SearchForm()
    results = {}
    
    if request.args.get('query'):
        query = request.args.get('query')
        category = request.args.get('category', 'all')
        
        form.query.data = query
        form.category.data = category
        
        if category in ['all', 'cases'] and current_user.is_authenticated:
            if current_user.role == 'lawyer':
                cases = Case.query.filter_by(lawyer_id=current_user.id).filter(
                    or_(Case.title.contains(query), Case.description.contains(query))
                ).limit(10).all()
            elif current_user.role == 'client':
                cases = Case.query.filter_by(client_id=current_user.id).filter(
                    or_(Case.title.contains(query), Case.description.contains(query))
                ).limit(10).all()
            else:
                cases = []
            results['cases'] = cases
        
        if category in ['all', 'courts']:
            courts = Court.query.filter_by(is_active=True).filter(
                or_(Court.name.contains(query), Court.city.contains(query))
            ).limit(10).all()
            results['courts'] = courts
        
        if category in ['all', 'lawyers']:
            lawyers = db.session.query(User, LawyerProfile).join(LawyerProfile).filter(
                User.role == 'lawyer',
                User.is_active == True,
                or_(User.first_name.contains(query), User.last_name.contains(query))
            ).limit(10).all()
            results['lawyers'] = lawyers
    
    return render_template('search.html', form=form, results=results)

# Admin Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with system overview"""
    from utils import admin_required, get_system_stats
    admin_required(lambda: None)()
    
    stats = get_system_stats()
    recent_activities = []  # You can add recent activities logic here
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_activities=recent_activities)

@app.route('/admin/dashboard/stats')
@login_required
def admin_dashboard_stats():
    """API endpoint for dashboard statistics"""
    from utils import admin_required, get_system_stats
    admin_required(lambda: None)()
    
    stats = get_system_stats()
    return jsonify(stats)

@app.route('/admin/users')
@login_required
def admin_users():
    """Admin user management page"""
    from utils import admin_required
    admin_required(lambda: None)()
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    
    query = User.query
    
    if search:
        query = query.filter(or_(
            User.first_name.contains(search),
            User.last_name.contains(search),
            User.username.contains(search),
            User.email.contains(search)
        ))
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    """Add new user"""
    from utils import admin_required, log_admin_activity
    from forms import AdminUserForm
    admin_required(lambda: None)()
    
    form = AdminUserForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            or_(User.username == form.username.data, User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل', 'danger')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                role=form.role.data,
                is_active=form.active.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            log_admin_activity('إضافة مستخدم', f'تم إضافة المستخدم: {user.full_name}')
            flash(f'تم إضافة المستخدم {user.full_name} بنجاح', 'success')
            return redirect(url_for('admin_users'))
    
    return render_template('admin/add_user.html', form=form)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """Edit user"""
    from utils import admin_required, log_admin_activity
    from forms import AdminUserForm
    admin_required(lambda: None)()
    
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    
    if form.validate_on_submit():
        # Check if username or email already exists (excluding current user)
        existing_user = User.query.filter(
            User.id != user_id,
            or_(User.username == form.username.data, User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل', 'danger')
        else:
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.phone = form.phone.data
            user.role = form.role.data
            user.is_active = form.active.data
            
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.commit()
            
            log_admin_activity('تعديل مستخدم', f'تم تعديل المستخدم: {user.full_name}')
            flash(f'تم تحديث بيانات المستخدم {user.full_name} بنجاح', 'success')
            return redirect(url_for('admin_users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Delete user"""
    from utils import admin_required, log_admin_activity
    admin_required(lambda: None)()
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص', 'danger')
        return redirect(url_for('admin_users'))
    
    user_name = user.full_name
    db.session.delete(user)
    db.session.commit()
    
    log_admin_activity('حذف مستخدم', f'تم حذف المستخدم: {user_name}')
    flash(f'تم حذف المستخدم {user_name} بنجاح', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/cases')
@login_required
def admin_cases():
    """Admin case management"""
    from utils import admin_required
    admin_required(lambda: None)()
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    
    query = Case.query
    
    if search:
        query = query.filter(or_(
            Case.title.contains(search),
            Case.case_number.contains(search),
            Case.description.contains(search)
        ))
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if type_filter:
        query = query.filter_by(case_type=type_filter)
    
    cases = query.order_by(Case.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/cases.html', cases=cases)

@app.route('/admin/cases/add', methods=['GET', 'POST'])
@login_required  
def admin_add_case():
    """Add new case"""
    from utils import admin_required, log_admin_activity, generate_case_number
    from forms import AdminCaseForm
    admin_required(lambda: None)()
    
    form = AdminCaseForm()
    
    # Populate choices
    form.lawyer_id.choices = [(0, 'اختر المحامي')] + [
        (u.id, u.full_name) for u in User.query.filter_by(role='lawyer', is_active=True).all()
    ]
    form.client_id.choices = [(0, 'اختر العميل')] + [
        (u.id, u.full_name) for u in User.query.filter_by(role='client', is_active=True).all()
    ]
    form.court_id.choices = [(0, 'اختر المحكمة')] + [
        (c.id, c.name) for c in Court.query.filter_by(is_active=True).all()
    ]
    
    if form.validate_on_submit():
        case = Case(
            case_number=form.case_number.data or generate_case_number(),
            title=form.title.data,
            description=form.description.data,
            case_type=form.case_type.data,
            lawyer_id=form.lawyer_id.data,
            client_id=form.client_id.data,
            court_id=form.court_id.data if form.court_id.data != 0 else None,
            status=form.status.data,
            priority=form.priority.data,
            filed_date=form.filed_date.data,
            next_hearing_date=form.next_hearing_date.data
        )
        db.session.add(case)
        db.session.commit()
        
        log_admin_activity('إضافة قضية', f'تم إضافة القضية: {case.title}')
        flash(f'تم إضافة القضية {case.title} بنجاح', 'success')
        return redirect(url_for('admin_cases'))
    
    return render_template('admin/add_case.html', form=form)

@app.route('/admin/courts')
@login_required
def admin_courts():
    """Admin court management"""
    from utils import admin_required
    admin_required(lambda: None)()
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    type_filter = request.args.get('type', '')
    governorate_filter = request.args.get('governorate', '')
    
    query = Court.query
    
    if search:
        query = query.filter(or_(
            Court.name.contains(search),
            Court.city.contains(search),
            Court.address.contains(search)
        ))
    
    if type_filter:
        query = query.filter_by(court_type=type_filter)
    
    if governorate_filter:
        query = query.filter_by(governorate=governorate_filter)
    
    courts = query.order_by(Court.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/courts.html', courts=courts)

@app.route('/admin/courts/add', methods=['GET', 'POST'])
@login_required
def admin_add_court():
    """Add new court"""
    from utils import admin_required, log_admin_activity
    from forms import AdminCourtForm
    admin_required(lambda: None)()
    
    form = AdminCourtForm()
    if form.validate_on_submit():
        court = Court(
            name=form.name.data,
            name_en=form.name_en.data,
            court_type=form.court_type.data,
            governorate=form.governorate.data,
            city=form.city.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            working_hours=form.working_hours.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            is_active=form.is_active.data
        )
        db.session.add(court)
        db.session.commit()
        
        log_admin_activity('إضافة محكمة', f'تم إضافة المحكمة: {court.name}')
        flash(f'تم إضافة المحكمة {court.name} بنجاح', 'success')
        return redirect(url_for('admin_courts'))
    
    return render_template('admin/add_court.html', form=form)

@app.route('/admin/lawyers')
@login_required
def admin_lawyers():
    """Admin lawyer management"""
    from utils import admin_required
    admin_required(lambda: None)()
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    verified_filter = request.args.get('verified', '')
    specialization_filter = request.args.get('specialization', '')
    
    query = db.session.query(User, LawyerProfile).join(LawyerProfile).filter(User.role == 'lawyer')
    
    if search:
        query = query.filter(or_(
            User.first_name.contains(search),
            User.last_name.contains(search),
            LawyerProfile.license_number.contains(search),
            LawyerProfile.law_firm.contains(search)
        ))
    
    if verified_filter == 'verified':
        query = query.filter(LawyerProfile.is_verified == True)
    elif verified_filter == 'unverified':
        query = query.filter(LawyerProfile.is_verified == False)
    
    if specialization_filter:
        query = query.filter(LawyerProfile.specialization == specialization_filter)
    
    lawyers = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/lawyers.html', lawyers=lawyers)

@app.route('/admin/appointments')
@login_required
def admin_appointments():
    """Admin appointment management"""
    from utils import admin_required
    admin_required(lambda: None)()
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    
    query = Appointment.query
    
    if search:
        query = query.filter(or_(
            Appointment.title.contains(search),
            Appointment.description.contains(search),
            Appointment.location.contains(search)
        ))
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if type_filter:
        query = query.filter_by(appointment_type=type_filter)
    
    appointments = query.order_by(Appointment.start_datetime.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/appointments.html', appointments=appointments)

@app.route('/admin/document-templates')
@login_required
def admin_document_templates():
    """Admin document template management"""
    from utils import admin_required
    admin_required(lambda: None)()
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    query = DocumentTemplate.query
    
    if search:
        query = query.filter(or_(
            DocumentTemplate.name.contains(search),
            DocumentTemplate.description.contains(search)
        ))
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    templates = query.order_by(DocumentTemplate.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/document_templates.html', templates=templates)

@app.route('/admin/system-settings')
@login_required
def admin_system_settings():
    """Admin system settings"""
    from utils import admin_required
    admin_required(lambda: None)()
    
    return render_template('admin/system_settings.html')

@app.route('/admin/reports')
@login_required
def admin_reports():
    """Admin reports and analytics"""
    from utils import admin_required, get_system_stats
    admin_required(lambda: None)()
    
    stats = get_system_stats()
    
    # Additional report data
    case_stats = {
        'by_type': db.session.query(Case.case_type, func.count(Case.id)).group_by(Case.case_type).all(),
        'by_status': db.session.query(Case.status, func.count(Case.id)).group_by(Case.status).all(),
        'by_month': db.session.query(
            func.extract('month', Case.created_at).label('month'),
            func.count(Case.id)
        ).group_by('month').all()
    }
    
    return render_template('admin/reports.html', stats=stats, case_stats=case_stats)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403
