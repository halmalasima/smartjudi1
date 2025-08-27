from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, EmailField, PasswordField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()], render_kw={"placeholder": "أدخل اسم المستخدم"})
    password = PasswordField('كلمة المرور', validators=[DataRequired()], render_kw={"placeholder": "أدخل كلمة المرور"})

class RegistrationForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "اختر اسم مستخدم"})
    email = EmailField('البريد الإلكتروني', validators=[DataRequired(), Email()], render_kw={"placeholder": "أدخل البريد الإلكتروني"})
    first_name = StringField('الاسم الأول', validators=[DataRequired()], render_kw={"placeholder": "الاسم الأول"})
    last_name = StringField('اسم العائلة', validators=[DataRequired()], render_kw={"placeholder": "اسم العائلة"})
    phone = StringField('رقم الهاتف', render_kw={"placeholder": "رقم الهاتف"})
    role = SelectField('الدور', choices=[
        ('client', 'متقاض'),
        ('lawyer', 'محامي'),
        ('judge', 'قاض'),
        ('student', 'طالب قانون')
    ], default='client')
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "كلمة المرور"})
    password2 = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "أكد كلمة المرور"})

class CourtForm(FlaskForm):
    name = StringField('اسم المحكمة', validators=[DataRequired()], render_kw={"placeholder": "اسم المحكمة"})
    name_en = StringField('الاسم بالإنجليزية', render_kw={"placeholder": "Court Name in English"})
    court_type = SelectField('نوع المحكمة', choices=[
        ('ابتدائية', 'محكمة ابتدائية'),
        ('استئناف', 'محكمة استئناف'),
        ('عليا', 'المحكمة العليا'),
        ('تجارية', 'محكمة تجارية'),
        ('جنائية', 'محكمة جنائية'),
        ('أحوال_شخصية', 'محكمة أحوال شخصية')
    ], validators=[DataRequired()])
    governorate = SelectField('المحافظة', choices=[
        ('صنعاء', 'صنعاء'),
        ('عدن', 'عدن'),
        ('تعز', 'تعز'),
        ('الحديدة', 'الحديدة'),
        ('إب', 'إب'),
        ('ذمار', 'ذمار'),
        ('حضرموت', 'حضرموت'),
        ('لحج', 'لحج'),
        ('أبين', 'أبين'),
        ('شبوة', 'شبوة'),
        ('مأرب', 'مأرب'),
        ('الجوف', 'الجوف'),
        ('صعدة', 'صعدة'),
        ('حجة', 'حجة'),
        ('المهرة', 'المهرة'),
        ('عمران', 'عمران'),
        ('الضالع', 'الضالع'),
        ('ريمة', 'ريمة'),
        ('البيضاء', 'البيضاء'),
        ('سقطرى', 'سقطرى')
    ], validators=[DataRequired()])
    city = StringField('المدينة', validators=[DataRequired()], render_kw={"placeholder": "المدينة"})
    address = TextAreaField('العنوان', render_kw={"placeholder": "العنوان التفصيلي"})
    phone = StringField('رقم الهاتف', render_kw={"placeholder": "رقم الهاتف"})
    email = EmailField('البريد الإلكتروني', validators=[Optional(), Email()], render_kw={"placeholder": "البريد الإلكتروني"})
    working_hours = TextAreaField('ساعات العمل', render_kw={"placeholder": "ساعات العمل"})

class LawyerProfileForm(FlaskForm):
    license_number = StringField('رقم الترخيص', validators=[DataRequired()], render_kw={"placeholder": "رقم ترخيص المحاماة"})
    specialization = SelectField('التخصص', choices=[
        ('مدني', 'قانون مدني'),
        ('جنائي', 'قانون جنائي'),
        ('تجاري', 'قانون تجاري'),
        ('عمالي', 'قانون عمل'),
        ('أحوال_شخصية', 'أحوال شخصية'),
        ('إداري', 'قانون إداري'),
        ('دستوري', 'قانون دستوري'),
        ('دولي', 'قانون دولي'),
        ('عقاري', 'قانون عقاري'),
        ('ضرائب', 'قانون ضرائب')
    ], validators=[DataRequired()])
    experience_years = IntegerField('سنوات الخبرة', validators=[Optional(), NumberRange(min=0, max=50)])
    law_firm = StringField('مكتب المحاماة', render_kw={"placeholder": "اسم مكتب المحاماة"})
    office_address = TextAreaField('عنوان المكتب', render_kw={"placeholder": "عنوان المكتب"})
    consultation_fee = FloatField('رسوم الاستشارة', validators=[Optional(), NumberRange(min=0)], render_kw={"placeholder": "رسوم الاستشارة بالريال"})
    bio = TextAreaField('نبذة تعريفية', render_kw={"placeholder": "نبذة عن الخبرة والتخصص"})

class CaseForm(FlaskForm):
    case_number = StringField('رقم القضية', validators=[DataRequired()], render_kw={"placeholder": "رقم القضية"})
    title = StringField('عنوان القضية', validators=[DataRequired()], render_kw={"placeholder": "عنوان القضية"})
    description = TextAreaField('وصف القضية', render_kw={"placeholder": "وصف تفصيلي للقضية"})
    case_type = SelectField('نوع القضية', choices=[
        ('مدني', 'مدني'),
        ('جنائي', 'جنائي'),
        ('تجاري', 'تجاري'),
        ('عمالي', 'عمالي'),
        ('أحوال_شخصية', 'أحوال شخصية'),
        ('إداري', 'إداري'),
        ('عقاري', 'عقاري'),
        ('ضرائب', 'ضرائب')
    ], validators=[DataRequired()])
    client_id = SelectField('العميل', coerce=int, validators=[DataRequired()])
    court_id = SelectField('المحكمة', coerce=int, validators=[Optional()])
    priority = SelectField('الأولوية', choices=[
        ('high', 'عالية'),
        ('medium', 'متوسطة'),
        ('low', 'منخفضة')
    ], default='medium')
    filed_date = DateField('تاريخ رفع القضية', validators=[DataRequired()])
    next_hearing_date = DateField('تاريخ الجلسة القادمة', validators=[Optional()])

class DocumentTemplateForm(FlaskForm):
    name = StringField('اسم النموذج', validators=[DataRequired()], render_kw={"placeholder": "اسم النموذج"})
    category = SelectField('الفئة', choices=[
        ('دعوى', 'دعوى'),
        ('عقد', 'عقد'),
        ('مذكرة', 'مذكرة'),
        ('طلب', 'طلب'),
        ('توكيل', 'توكيل'),
        ('إقرار', 'إقرار'),
        ('شهادة', 'شهادة')
    ], validators=[DataRequired()])
    description = TextAreaField('الوصف', render_kw={"placeholder": "وصف النموذج"})
    template_content = TextAreaField('محتوى النموذج', validators=[DataRequired()], 
                                   widget=TextArea(), 
                                   render_kw={"rows": 15, "placeholder": "محتوى النموذج"})

class DocumentUploadForm(FlaskForm):
    title = StringField('عنوان المستند', validators=[DataRequired()], render_kw={"placeholder": "عنوان المستند"})
    description = TextAreaField('الوصف', render_kw={"placeholder": "وصف المستند"})
    document_type = SelectField('نوع المستند', choices=[
        ('evidence', 'دليل'),
        ('contract', 'عقد'),
        ('court_order', 'أمر محكمة'),
        ('petition', 'عريضة'),
        ('correspondence', 'مراسلات'),
        ('other', 'أخرى')
    ], validators=[DataRequired()])
    file = FileField('الملف', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'الملفات المسموحة: PDF, DOC, DOCX, JPG, PNG')
    ])
    case_id = SelectField('القضية', coerce=int, validators=[Optional()])

class AppointmentForm(FlaskForm):
    title = StringField('العنوان', validators=[DataRequired()], render_kw={"placeholder": "عنوان الموعد"})
    description = TextAreaField('الوصف', render_kw={"placeholder": "وصف الموعد"})
    appointment_type = SelectField('نوع الموعد', choices=[
        ('hearing', 'جلسة محكمة'),
        ('meeting', 'اجتماع'),
        ('deadline', 'موعد نهائي'),
        ('consultation', 'استشارة'),
        ('court_visit', 'زيارة محكمة')
    ], validators=[DataRequired()])
    start_datetime = StringField('التاريخ والوقت', validators=[DataRequired()], 
                                render_kw={"type": "datetime-local"})
    end_datetime = StringField('وقت الانتهاء', validators=[Optional()], 
                              render_kw={"type": "datetime-local"})
    is_all_day = BooleanField('طوال اليوم')
    case_id = SelectField('القضية', coerce=int, validators=[Optional()])
    location = StringField('المكان', render_kw={"placeholder": "مكان الموعد"})
    reminder_minutes = SelectField('تذكير قبل', choices=[
        (15, '15 دقيقة'),
        (30, '30 دقيقة'),
        (60, 'ساعة'),
        (120, 'ساعتين'),
        (1440, 'يوم'),
        (2880, 'يومين')
    ], default=60, coerce=int)

class SearchForm(FlaskForm):
    query = StringField('البحث', render_kw={"placeholder": "ابحث..."})
    category = SelectField('الفئة', choices=[
        ('all', 'الكل'),
        ('cases', 'القضايا'),
        ('courts', 'المحاكم'),
        ('lawyers', 'المحامين'),
        ('documents', 'المستندات')
    ], default='all')

# Admin Forms
class AdminUserForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "اسم المستخدم"})
    email = EmailField('البريد الإلكتروني', validators=[DataRequired(), Email()], render_kw={"placeholder": "البريد الإلكتروني"})
    first_name = StringField('الاسم الأول', validators=[DataRequired()], render_kw={"placeholder": "الاسم الأول"})
    last_name = StringField('اسم العائلة', validators=[DataRequired()], render_kw={"placeholder": "اسم العائلة"})
    phone = StringField('رقم الهاتف', render_kw={"placeholder": "رقم الهاتف"})
    role = SelectField('الدور', choices=[
        ('admin', 'مدير النظام'),
        ('judge', 'قاض'),
        ('lawyer', 'محامي'),
        ('client', 'متقاض'),
        ('student', 'طالب قانون')
    ], validators=[DataRequired()])
    active = BooleanField('نشط', default=True)
    password = PasswordField('كلمة المرور', validators=[Optional(), Length(min=6)], render_kw={"placeholder": "كلمة المرور (اتركها فارغة للاحتفاظ بالحالية)"})

class AdminCaseForm(FlaskForm):
    case_number = StringField('رقم القضية', validators=[DataRequired()], render_kw={"placeholder": "رقم القضية"})
    title = StringField('عنوان القضية', validators=[DataRequired()], render_kw={"placeholder": "عنوان القضية"})
    description = TextAreaField('وصف القضية', render_kw={"placeholder": "وصف تفصيلي للقضية"})
    case_type = SelectField('نوع القضية', choices=[
        ('مدني', 'مدني'),
        ('جنائي', 'جنائي'),
        ('تجاري', 'تجاري'),
        ('عمالي', 'عمالي'),
        ('أحوال_شخصية', 'أحوال شخصية'),
        ('إداري', 'إداري'),
        ('عقاري', 'عقاري'),
        ('ضرائب', 'ضرائب')
    ], validators=[DataRequired()])
    lawyer_id = SelectField('المحامي', coerce=int, validators=[DataRequired()])
    client_id = SelectField('العميل', coerce=int, validators=[DataRequired()])
    court_id = SelectField('المحكمة', coerce=int, validators=[Optional()])
    status = SelectField('الحالة', choices=[
        ('active', 'نشطة'),
        ('pending', 'معلقة'),
        ('closed', 'مغلقة')
    ], default='active')
    priority = SelectField('الأولوية', choices=[
        ('high', 'عالية'),
        ('medium', 'متوسطة'),
        ('low', 'منخفضة')
    ], default='medium')
    filed_date = DateField('تاريخ رفع القضية', validators=[DataRequired()])
    next_hearing_date = DateField('تاريخ الجلسة القادمة', validators=[Optional()])

class AdminCourtForm(FlaskForm):
    name = StringField('اسم المحكمة', validators=[DataRequired()], render_kw={"placeholder": "اسم المحكمة"})
    name_en = StringField('الاسم بالإنجليزية', render_kw={"placeholder": "Court Name in English"})
    court_type = SelectField('نوع المحكمة', choices=[
        ('ابتدائية', 'محكمة ابتدائية'),
        ('استئناف', 'محكمة استئناف'),
        ('عليا', 'المحكمة العليا'),
        ('تجارية', 'محكمة تجارية'),
        ('جنائية', 'محكمة جنائية'),
        ('أحوال_شخصية', 'محكمة أحوال شخصية')
    ], validators=[DataRequired()])
    governorate = SelectField('المحافظة', choices=[
        ('صنعاء', 'صنعاء'), ('عدن', 'عدن'), ('تعز', 'تعز'), ('الحديدة', 'الحديدة'),
        ('إب', 'إب'), ('ذمار', 'ذمار'), ('حضرموت', 'حضرموت'), ('لحج', 'لحج'),
        ('أبين', 'أبين'), ('شبوة', 'شبوة'), ('مأرب', 'مأرب'), ('الجوف', 'الجوف'),
        ('صعدة', 'صعدة'), ('حجة', 'حجة'), ('المهرة', 'المهرة'), ('عمران', 'عمران'),
        ('الضالع', 'الضالع'), ('ريمة', 'ريمة'), ('البيضاء', 'البيضاء'), ('سقطرى', 'سقطرى')
    ], validators=[DataRequired()])
    city = StringField('المدينة', validators=[DataRequired()], render_kw={"placeholder": "المدينة"})
    address = TextAreaField('العنوان', render_kw={"placeholder": "العنوان التفصيلي"})
    phone = StringField('رقم الهاتف', render_kw={"placeholder": "رقم الهاتف"})
    email = EmailField('البريد الإلكتروني', validators=[Optional(), Email()], render_kw={"placeholder": "البريد الإلكتروني"})
    working_hours = TextAreaField('ساعات العمل', render_kw={"placeholder": "ساعات العمل"})
    latitude = FloatField('خط العرض', validators=[Optional()], render_kw={"placeholder": "خط العرض"})
    longitude = FloatField('خط الطول', validators=[Optional()], render_kw={"placeholder": "خط الطول"})
    is_active = BooleanField('نشط', default=True)

class AdminLawyerForm(FlaskForm):
    user_id = SelectField('المستخدم', coerce=int, validators=[DataRequired()])
    license_number = StringField('رقم الترخيص', validators=[DataRequired()], render_kw={"placeholder": "رقم ترخيص المحاماة"})
    specialization = SelectField('التخصص', choices=[
        ('مدني', 'قانون مدني'), ('جنائي', 'قانون جنائي'), ('تجاري', 'قانون تجاري'),
        ('عمالي', 'قانون عمل'), ('أحوال_شخصية', 'أحوال شخصية'), ('إداري', 'قانون إداري'),
        ('دستوري', 'قانون دستوري'), ('دولي', 'قانون دولي'), ('عقاري', 'قانون عقاري'),
        ('ضرائب', 'قانون ضرائب')
    ], validators=[DataRequired()])
    experience_years = IntegerField('سنوات الخبرة', validators=[Optional(), NumberRange(min=0, max=50)])
    law_firm = StringField('مكتب المحاماة', render_kw={"placeholder": "اسم مكتب المحاماة"})
    office_address = TextAreaField('عنوان المكتب', render_kw={"placeholder": "عنوان المكتب"})
    consultation_fee = FloatField('رسوم الاستشارة', validators=[Optional(), NumberRange(min=0)], render_kw={"placeholder": "رسوم الاستشارة بالريال"})
    bio = TextAreaField('نبذة تعريفية', render_kw={"placeholder": "نبذة عن الخبرة والتخصص"})
    is_verified = BooleanField('محامي معتمد', default=False)
    rating = FloatField('التقييم', validators=[Optional(), NumberRange(min=0, max=5)], render_kw={"placeholder": "التقييم من 0 إلى 5"})

class AdminAppointmentForm(FlaskForm):
    title = StringField('العنوان', validators=[DataRequired()], render_kw={"placeholder": "عنوان الموعد"})
    description = TextAreaField('الوصف', render_kw={"placeholder": "وصف الموعد"})
    appointment_type = SelectField('نوع الموعد', choices=[
        ('hearing', 'جلسة محكمة'),
        ('meeting', 'اجتماع'),
        ('deadline', 'موعد نهائي'),
        ('consultation', 'استشارة'),
        ('court_visit', 'زيارة محكمة')
    ], validators=[DataRequired()])
    user_id = SelectField('المستخدم', coerce=int, validators=[DataRequired()])
    case_id = SelectField('القضية', coerce=int, validators=[Optional()])
    start_datetime = StringField('التاريخ والوقت', validators=[DataRequired()], 
                                render_kw={"type": "datetime-local"})
    end_datetime = StringField('وقت الانتهاء', validators=[Optional()], 
                              render_kw={"type": "datetime-local"})
    is_all_day = BooleanField('طوال اليوم')
    location = StringField('المكان', render_kw={"placeholder": "مكان الموعد"})
    status = SelectField('الحالة', choices=[
        ('scheduled', 'مجدول'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي')
    ], default='scheduled')
    reminder_minutes = SelectField('تذكير قبل', choices=[
        (15, '15 دقيقة'), (30, '30 دقيقة'), (60, 'ساعة'),
        (120, 'ساعتين'), (1440, 'يوم'), (2880, 'يومين')
    ], default=60, coerce=int)

class AdminDocumentTemplateForm(FlaskForm):
    name = StringField('اسم النموذج', validators=[DataRequired()], render_kw={"placeholder": "اسم النموذج"})
    category = SelectField('الفئة', choices=[
        ('دعوى', 'دعوى'), ('عقد', 'عقد'), ('مذكرة', 'مذكرة'),
        ('طلب', 'طلب'), ('توكيل', 'توكيل'), ('إقرار', 'إقرار'), ('شهادة', 'شهادة')
    ], validators=[DataRequired()])
    description = TextAreaField('الوصف', render_kw={"placeholder": "وصف النموذج"})
    template_content = TextAreaField('محتوى النموذج', validators=[DataRequired()], 
                                   widget=TextArea(), 
                                   render_kw={"rows": 15, "placeholder": "محتوى النموذج"})
    template_fields = TextAreaField('الحقول القابلة للتعبئة', render_kw={"placeholder": "الحقول بتنسيق JSON"})
    is_active = BooleanField('نشط', default=True)
    created_by = SelectField('منشئ النموذج', coerce=int, validators=[DataRequired()])
